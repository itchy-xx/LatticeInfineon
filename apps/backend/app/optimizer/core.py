"""Refactored, callable duplicate of legacy/lattice_optimizer.py's scoring/selection engine.

WHY THIS FILE EXISTS INSTEAD OF EDITING THE LEGACY SCRIPT: the integration task asked for
lattice_optimizer.py to be refactored in place into functions. Per explicit instruction, that
file must not be edited at all -- it is kept byte-identical in legacy/lattice_optimizer.py as
the standalone batch-processing entry point. This module instead duplicates its formulas and
control flow (copied statement-for-statement, not reinterpreted or approximated) inside plain
functions that take explicit parameters instead of reading/mutating module-level globals, so a
web request can run a scenario against a private copy of the hub-constraints table without any
cross-request shared mutable state. apps/backend/tests/test_optimizer_regression.py imports the
legacy module fresh and asserts this file reproduces its results exactly for every scenario the
legacy script supports (Normal/PrimaryHubDown/AirCapacityReduced) -- any accidental divergence
between the two fails that test. Do not "improve" or simplify formulas here without mirroring
the identical change in legacy/lattice_optimizer.py's own docstring reasoning (A1-A26) first --
this file's entire purpose is to be provably equivalent to that script, not merely inspired by it.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

W_LEAD, W_COST, W_RISK = 0.40, 0.40, 0.20
L_MIN, L_MAX = 1, 12
C_MIN, C_MAX = 145, 886
R_MIN, R_MAX = 0.6, 4.7
HAZ_PENALTY = 1.5
DISRUPT_PENALTY = 0.5
SHELF_PENALTY = 1.5
HUB_CRISIS_WEEKS = 52
COST_CLIP_DISCLOSE_RATIO = 2.0
MAX_SPLIT_SIBLINGS = 2
PRIORITY_WEIGHTS = {
    "Standard": (0.40, 0.40, 0.20),
    "Expedite": (0.60, 0.20, 0.20),
    "Critical": (0.55, 0.10, 0.35),
}
SCENARIOS = ["Normal", "PrimaryHubDown", "AirCapacityReduced"]
PRIO = {"Expedite": 0, "Critical": 1, "Standard": 2}


# ---------- hub disruption state (A5/A26) ----------
def set_hub_disruption_state(hc: pd.DataFrame, scen: str) -> tuple[pd.DataFrame, set]:
    """Returns a FRESH hub frame (copy of hc, indexed by HubID, with headroom/disrupted
    columns) plus the resulting dead_hubs set -- never mutates hc or any shared frame, so
    concurrent requests/scenarios never see each other's state (unlike legacy's module-level
    `hub`/`dead_hubs` mutation via this same-named function)."""
    hub = hc.set_index("HubID").copy()
    red = hub.CapacityReductionPct if scen != "Normal" else 0
    hub["headroom"] = (hub.WeeklyCapacityUnits * (hub.MaxUtilizationPct - red)
                        - hub.WeeklyCapacityUnits * hub.CurrentUtilizationPct).clip(lower=0)
    hub["disrupted"] = red > 0 if scen != "Normal" else False
    dead_hubs = set(hub[hub.headroom <= 0].index)
    return hub, dead_hubs


def apply_hub_overrides(hc: pd.DataFrame, overrides: dict[str, dict]) -> pd.DataFrame:
    """Simulation adapters (port congestion / cold-chain restriction) call this to get a
    private copy of Hub_Constraints with specific fields overridden for specific HubIDs,
    fed into set_hub_disruption_state() exactly as the unmodified sheet would be. Never
    writes back to the loaded OptimizerData.hc -- copy-on-write only."""
    hc2 = hc.copy()
    idx = hc2.set_index("HubID").index
    for hub_id, fields in overrides.items():
        if hub_id not in idx:
            continue
        mask = hc2.HubID == hub_id
        for col, val in fields.items():
            hc2.loc[mask, col] = val
    return hc2


# ---------- route availability (A6) ----------
def routes_available_in(ro: pd.DataFrame, scen: str) -> pd.DataFrame:
    if scen == "Normal":
        return ro[ro.AvailableFlag == "Yes"]
    return ro[(ro.DisruptionScenario == scen) & (ro.AvailableFlag == "Yes")]


def hub_pass(hub: pd.DataFrame, h: str, hz: str | None) -> bool:
    r = hub.loc[h]
    if hz == "ESD Sensitive" and r.ESDHandlingAvailable != "Yes":
        return False
    if hz == "Moisture Sensitive" and r.MoistureControlAvailable != "Yes":
        return False
    if hz == "Lithium Handling" and r.LithiumHandlingAvailable != "Yes":
        return False
    return True


def queue_weeks_for(committed_before: float, cap: float) -> int:
    return int(committed_before) // int(cap) if cap > 0 else 99


def eff_lead(base_lead: float, qty: float, cap: float, committed_before: float = 0.0,
             hub_queue_weeks: int = 0) -> float:
    weeks = math.ceil(qty / cap) if cap > 0 else 99
    combined_queue = max(queue_weeks_for(committed_before, cap), hub_queue_weeks)
    return base_lead + 7 * (combined_queue + weeks - 1)


def hub_qweeks(hub: pd.DataFrame, h: str, committed_hub_dict: dict) -> int:
    return queue_weeks_for(committed_hub_dict.get(h, 0.0), hub.loc[h].headroom)


def combined_hub_qweeks(hub: pd.DataFrame, from_h: str, to_h: str, committed_hub_dict: dict) -> int:
    return max(hub_qweeks(hub, from_h, committed_hub_dict), hub_qweeks(hub, to_h, committed_hub_dict))


def commit_hub_usage(from_h: str, to_h: str, qty: float, committed_hub_dict: dict, split=None) -> None:
    if split:
        siblings = split["siblings"]
        from_sib_qty = sum(sb["sibling_qty"] for sb in siblings if sb["side"] == "From")
        to_sib_qty = sum(sb["sibling_qty"] for sb in siblings if sb["side"] == "To")
        committed_hub_dict[from_h] = committed_hub_dict.get(from_h, 0.0) + (qty - from_sib_qty)
        committed_hub_dict[to_h] = committed_hub_dict.get(to_h, 0.0) + (qty - to_sib_qty)
        for sb in siblings:
            committed_hub_dict[sb["sibling"]] = committed_hub_dict.get(sb["sibling"], 0.0) + sb["sibling_qty"]
    else:
        committed_hub_dict[from_h] = committed_hub_dict.get(from_h, 0.0) + qty
        committed_hub_dict[to_h] = committed_hub_dict.get(to_h, 0.0) + qty


# ---------- A14 cross-family donors ----------
def pick_best_hub(hub: pd.DataFrame, dead_hubs: set, hub_ids: list[str]) -> str | None:
    alive = [h for h in hub_ids if h not in dead_hubs]
    if not alive:
        return None
    non_disrupted = [h for h in alive if not hub.loc[h].disrupted]
    return non_disrupted[0] if non_disrupted else alive[0]


def cross_family_candidates(hub: pd.DataFrame, dead_hubs: set, hubs_by_stage_country: dict,
                             donor_cache: dict, ro: pd.DataFrame, sf: str, st: str, scen: str,
                             hz: str | None, cold: bool, from_country: str, to_country: str) -> list:
    key = (sf, st, scen)
    if key not in donor_cache:
        avail = routes_available_in(ro, scen)
        all_routes = avail[(avail.StageFrom == sf) & (avail.StageTo == st)]
        donors: dict = {}
        for _, row in all_routes.iterrows():
            ck = (hub.loc[row.FromHub].Country, hub.loc[row.ToHub].Country)
            if ck not in donors or row.BaseCostEUR < donors[ck].BaseCostEUR:
                donors[ck] = row
        donor_cache[key] = donors
    donor = donor_cache[key].get((from_country, to_country))
    if donor is None:
        return []
    from_ok = [h for h in hubs_by_stage_country.get((sf, from_country), [])
               if (not cold or hub.loc[h].ColdChainAvailable == "Yes") and hub_pass(hub, h, hz)]
    to_ok = [h for h in hubs_by_stage_country.get((st, to_country), [])
             if (not cold or hub.loc[h].ColdChainAvailable == "Yes") and hub_pass(hub, h, hz)]
    fh, th = pick_best_hub(hub, dead_hubs, from_ok), pick_best_hub(hub, dead_hubs, to_ok)
    if fh is None or th is None:
        return []
    return [pd.Series(dict(
        RouteOptionID=f"XF-{donor.RouteOptionID}-{fh}-{th}", FromHub=fh, ToHub=th,
        TransportMode=donor.TransportMode, BaseLeadTimeDays=donor.BaseLeadTimeDays,
        BaseCostEUR=donor.BaseCostEUR, CapacityUnitsPerWeek=donor.CapacityUnitsPerWeek,
        RiskScore=donor.RiskScore, CO2Kg=donor.CO2Kg, IsCrossFamily=True))]


def sibling_hubs(hub: pd.DataFrame, dead_hubs: set, hubs_by_stage_city: dict, stage: str,
                  city: str, exclude_hub: str, hz: str | None, cold: bool) -> list[str]:
    return [h for h in hubs_by_stage_city.get((stage, city), [])
            if h != exclude_hub and h not in dead_hubs
            and (not cold or hub.loc[h].ColdChainAvailable == "Yes") and hub_pass(hub, h, hz)]


def try_hub_split(hub: pd.DataFrame, dead_hubs: set, hubs_by_stage_city: dict, sf: str, st: str,
                   r, qty: float, committed_r: float, hz: str | None, cold: bool,
                   committed_hub: dict) -> list[dict]:
    cap = r.CapacityUnitsPerWeek
    weeks_single = queue_weeks_for(committed_r, cap) + math.ceil(qty / cap)
    if weeks_single <= 1:
        return []
    candidates = []
    seen_hubs = {r.FromHub, r.ToHub}
    for side, h0, stage in [("From", r.FromHub, sf), ("To", r.ToHub, st)]:
        city = hub.loc[h0].City
        for sib in sibling_hubs(hub, dead_hubs, hubs_by_stage_city, stage, city, h0, hz, cold):
            if sib in seen_hubs:
                continue
            seen_hubs.add(sib)
            avail = hub.loc[sib].headroom - committed_hub.get(sib, 0.0)
            if avail > 0:
                candidates.append((avail, sib, side))
    if not candidates:
        return []
    candidates.sort(key=lambda x: -x[0])

    options = []
    for n in range(1, min(MAX_SPLIT_SIBLINGS, len(candidates)) + 1):
        chosen = candidates[:n]
        combined_cap = cap + sum(min(avail, cap) for avail, sib, side in chosen)
        weeks_split = queue_weeks_for(committed_r, combined_cap) + math.ceil(qty / combined_cap)
        if weeks_split >= weeks_single:
            continue
        siblings = [dict(sibling=sib, side=side, sibling_qty=round(qty * (min(avail, cap) / combined_cap)))
                    for avail, sib, side in chosen]
        siblings = [sb for sb in siblings if sb["sibling_qty"] > 0]
        if siblings:
            options.append(dict(weeks=weeks_split, weeks_single=weeks_single, siblings=siblings))
    return options


def score(lead: float, cost: float, risk: float) -> float:
    nl = max(0.0, min(1.0, (lead - L_MIN) / (L_MAX - L_MIN)))
    nc = max(0.0, min(1.0, (cost - C_MIN) / (C_MAX - C_MIN)))
    nr = max(0.0, min(1.0, (risk - R_MIN) / (R_MAX - R_MIN)))
    return W_LEAD * nl + W_COST * nc + W_RISK * nr


def score_priority(lead: float, cost: float, risk: float, priority: str) -> float:
    wl, wc, wr = PRIORITY_WEIGHTS[priority]
    nl = max(0.0, min(1.0, (lead - L_MIN) / (L_MAX - L_MIN)))
    nc = max(0.0, min(1.0, (cost - C_MIN) / (C_MAX - C_MIN)))
    nr = max(0.0, min(1.0, (risk - R_MIN) / (R_MAX - R_MIN)))
    return wl * nl + wc * nc + wr * nr


def score_cpk(lead: float, cpk: float, risk: float, cpk_min: float, cpk_max: float) -> float:
    nl = max(0.0, min(1.0, (lead - L_MIN) / (L_MAX - L_MIN)))
    nc = max(0.0, min(1.0, (cpk - cpk_min) / (cpk_max - cpk_min)))
    nr = max(0.0, min(1.0, (risk - R_MIN) / (R_MAX - R_MIN)))
    return W_LEAD * nl + W_COST * nc + W_RISK * nr


def score_cpk_priority(lead: float, cpk: float, risk: float, priority: str, cpk_min: float, cpk_max: float) -> float:
    wl, wc, wr = PRIORITY_WEIGHTS[priority]
    nl = max(0.0, min(1.0, (lead - L_MIN) / (L_MAX - L_MIN)))
    nc = max(0.0, min(1.0, (cpk - cpk_min) / (cpk_max - cpk_min)))
    nr = max(0.0, min(1.0, (risk - R_MIN) / (R_MAX - R_MIN)))
    return wl * nl + wc * nc + wr * nr


def run_internal_scenario(data, hub: pd.DataFrame, dead_hubs: set, scen: str) -> pd.DataFrame:
    """Mirrors legacy's `for scen in SCENARIOS:` Internal_Shipments body exactly, for ONE
    scenario, taking `hub`/`dead_hubs` as parameters (private per-call state) instead of
    reading/mutating module globals. `data` is an OptimizerData bundle (see data_loader.py)."""
    ints, mat, ro = data.ints, data.mat, data.ro
    hubs_by_stage_country, hubs_by_stage_city = data.hubs_by_stage_country, data.hubs_by_stage_city
    primary, primary_ids = data.primary, data.primary_ids
    groups = data.cand_by_scen[scen]
    donor_cache: dict = {}

    work = ints.copy()
    work["prio"] = work.MaterialNo_Anon.map(lambda m: PRIO[mat.loc[m].PriorityClass])
    work = work.sort_values(["prio", "ShipDate"])

    committed, committed_baseline, committed_hub, committed_baseline_hub = {}, {}, {}, {}
    rows = []

    for _, s in work.iterrows():
        m = mat.loc[s.MaterialNo_Anon]
        hz = m.HazardClass if isinstance(m.HazardClass, str) else None
        cold = m.TempRequirement == "Cold Chain"
        shelf_life = m.ShelfLifeDays
        key = (s.MaterialFamily, s.StageFrom, s.StageTo)
        try:
            cc = groups.get_group(key)
        except KeyError:
            cc = pd.DataFrame()

        own_primary_id = None
        try:
            p = primary.loc[(s.MaterialFamily, s.StageFrom, s.StageTo, s.ShipFrom_Alias, s.ShipTo_Alias)]
            if isinstance(p, pd.DataFrame):
                p = p.iloc[0]
            own_primary_id = p.RouteOptionID
            b_committed = committed_baseline.get(p.RouteOptionID, 0.0)
            b_hub_qw = combined_hub_qweeks(hub, s.ShipFrom_Alias, s.ShipTo_Alias, committed_baseline_hub)
            b_lead = eff_lead(p.BaseLeadTimeDays, s.Qty, p.CapacityUnitsPerWeek, b_committed, b_hub_qw)
            committed_baseline[p.RouteOptionID] = b_committed + s.Qty
            commit_hub_usage(s.ShipFrom_Alias, s.ShipTo_Alias, s.Qty, committed_baseline_hub)
            b_cost, b_risk = float(p.BaseCostEUR), float(p.RiskScore)
            if hub.loc[s.ShipFrom_Alias].disrupted or hub.loc[s.ShipTo_Alias].disrupted:
                b_risk += DISRUPT_PENALTY
            if not (hub_pass(hub, s.ShipFrom_Alias, hz) and hub_pass(hub, s.ShipTo_Alias, hz)):
                b_risk += HAZ_PENALTY
            if cold and not (hub.loc[s.ShipFrom_Alias].ColdChainAvailable == "Yes"
                              and hub.loc[s.ShipTo_Alias].ColdChainAvailable == "Yes"):
                b_risk += HAZ_PENALTY
            if b_lead > shelf_life:
                b_risk += SHELF_PENALTY
        except KeyError:
            b_lead = b_cost = b_risk = np.nan

        best, best_key, waiver, is_cross_family_fallback = None, None, False, False

        def _filter_into_pools(candidates):
            ps, pw = [], []
            for r in candidates:
                if r.FromHub in dead_hubs or r.ToHub in dead_hubs:
                    continue
                cold_ok = (not cold) or (hub.loc[r.FromHub].ColdChainAvailable == "Yes"
                                          and hub.loc[r.ToHub].ColdChainAvailable == "Yes")
                if not cold_ok:
                    continue
                haz_ok = hub_pass(hub, r.FromHub, hz) and hub_pass(hub, r.ToHub, hz)
                (ps if haz_ok else pw).append(r)
            return ps, pw

        pool_strict, pool_waiver = _filter_into_pools([r for _, r in cc.iterrows()])
        if not pool_strict and not pool_waiver:
            cf_candidates = cross_family_candidates(
                hub, dead_hubs, hubs_by_stage_country, donor_cache, ro,
                s.StageFrom, s.StageTo, scen, hz, cold,
                hub.loc[s.ShipFrom_Alias].Country, hub.loc[s.ShipTo_Alias].Country)
            pool_strict, pool_waiver = _filter_into_pools(cf_candidates)
            is_cross_family_fallback = bool(pool_strict or pool_waiver)
        pool = pool_strict if pool_strict else pool_waiver
        waiver = not pool_strict and bool(pool_waiver)

        candidates_scored = []
        for r in pool:
            r_committed = committed.get(r.RouteOptionID, 0.0)
            hub_qw = combined_hub_qweeks(hub, r.FromHub, r.ToHub, committed_hub)
            lead = eff_lead(r.BaseLeadTimeDays, s.Qty, r.CapacityUnitsPerWeek, r_committed, hub_qw)
            base_risk = float(r.RiskScore) + (HAZ_PENALTY if waiver else 0.0) \
                + (DISRUPT_PENALTY if (hub.loc[r.FromHub].disrupted or hub.loc[r.ToHub].disrupted) else 0.0)
            on_time = lead <= shelf_life
            risk = base_risk + (0.0 if on_time else SHELF_PENALTY)
            sc = score(lead, r.BaseCostEUR, risk)
            candidates_scored.append((r, lead, base_risk, risk, sc, on_time))

        on_time_pool = [c for c in candidates_scored if c[5]]
        eval_pool = on_time_pool if on_time_pool else candidates_scored
        all_lead_capped = all(c[1] > L_MAX for c in eval_pool)
        all_risk_capped = all(c[3] > R_MAX for c in eval_pool)
        for r, lead, base_risk, risk, sc, on_time in eval_pool:
            if all_lead_capped:
                k = (lead, sc, r.BaseCostEUR, risk)
            elif all_risk_capped:
                k = (risk, sc, r.BaseCostEUR, lead)
            else:
                k = (sc, r.BaseCostEUR, risk)
            if best is None or k < best_key:
                best, best_key = (r, lead, base_risk, risk), k

        if best is None:
            rows.append(dict(ShipmentID=s.ShipmentID, Scenario=scen, Priority=m.PriorityClass,
                              Qty=s.Qty, RouteOptionID="", FromHub="", ToHub="", Mode="",
                              EffLead=None, Cost=None, RiskAdj=None, CO2=None,
                              BLead=b_lead, BCost=b_cost, BRisk=b_risk, PriorityScore=None,
                              StrictComplianceSolved="No",
                              Solved="No", Notes="UNSOLVED — no compliant lane found (native or cross-family); escalate"))
            continue

        r, lead, base_risk, risk = best
        crisis_hub, crisis_hub_qw = None, 0
        for hh in (r.FromHub, r.ToHub):
            hh_qw = hub_qweeks(hub, hh, committed_hub)
            if hh_qw > crisis_hub_qw:
                crisis_hub, crisis_hub_qw = hh, hh_qw
        r_committed = committed.get(r.RouteOptionID, 0.0)
        single_cost = float(r.BaseCostEUR)
        single_score = score(lead, single_cost, risk)
        split_options = try_hub_split(hub, dead_hubs, hubs_by_stage_city, s.StageFrom, s.StageTo,
                                       r, s.Qty, r_committed, hz, cold, committed_hub)
        best_opt = None
        for opt in split_options:
            opt_lead = float(r.BaseLeadTimeDays) + 7 * (opt["weeks"] - 1)
            opt_on_time = opt_lead <= shelf_life
            opt_risk = base_risk + (0.0 if opt_on_time else SHELF_PENALTY)
            opt_sib_qty = sum(sb["sibling_qty"] for sb in opt["siblings"])
            opt_extra_cost = sum(hub.loc[sb["sibling"]].FixedHandlingCost_EUR
                                  + hub.loc[sb["sibling"]].VariableHandlingCostPerUnit_EUR * sb["sibling_qty"]
                                  for sb in opt["siblings"])
            opt_cost = single_cost + opt_extra_cost
            opt_score = score(opt_lead, opt_cost, opt_risk)
            if opt_score < single_score and (best_opt is None or opt_score < best_opt["score"]):
                best_opt = dict(split=opt, lead=opt_lead, risk=opt_risk, cost=opt_cost,
                                 sib_qty=opt_sib_qty, score=opt_score)
        use_split = best_opt is not None
        notes = []
        if use_split:
            split, sib_qty = best_opt["split"], best_opt["sib_qty"]
            lead, cost, risk = best_opt["lead"], best_opt["cost"], best_opt["risk"]
            lane_qty = s.Qty - sib_qty
            committed[r.RouteOptionID] = r_committed + lane_qty
            commit_hub_usage(r.FromHub, r.ToHub, s.Qty, committed_hub, split=split)
            n_sib = len(split["siblings"])
            sib_desc = "; ".join(f"{int(sb['sibling_qty'])}u via {sb['sibling']} ({sb['side']} side)"
                                  for sb in split["siblings"])
            split_note = (f"hub split ({n_sib}-way): {sib_desc} -- cuts to {split['weeks']} wk(s) "
                          f"from {split['weeks_single']} single-hub; downstream DCA consolidation effort "
                          f"not modeled, human review recommended" +
                          (f"; {n_sib} extra hubs used -- real coordination overhead scales with hub "
                           f"count (A24, bounded at {MAX_SPLIT_SIBLINGS}), weigh against the lead-time "
                           f"gain before approving" if n_sib > 1 else ""))
            if cost > C_MAX and single_cost > 0 and cost / single_cost >= COST_CLIP_DISCLOSE_RATIO:
                split_note += (f"; COST-CLIP CAUTION: real split cost is "
                               f"{cost/single_cost:.1f}x the single-hub fee -- cost normalizes "
                               f"the same past EUR{C_MAX:.0f} regardless of magnitude, so the score "
                               f"cannot distinguish this from a smaller overage; verify the true euro "
                               f"tradeoff before approving")
            notes.append(split_note)
        else:
            cost = single_cost
            committed[r.RouteOptionID] = r_committed + s.Qty
            commit_hub_usage(r.FromHub, r.ToHub, s.Qty, committed_hub)
            queue_weeks = queue_weeks_for(r_committed, r.CapacityUnitsPerWeek)
            if queue_weeks > 0:
                notes.append(f"capacity contention: queued {queue_weeks} wk(s) behind higher-priority demand")
            if math.ceil(s.Qty / r.CapacityUnitsPerWeek) > 1:
                notes.append(f"multi-week split ({math.ceil(s.Qty/r.CapacityUnitsPerWeek)} wks)")
        if waiver:
            notes.append("hazard waiver +1.5 risk — manual review")
        if hub.loc[r.FromHub].disrupted or hub.loc[r.ToHub].disrupted:
            notes.append("disrupted hub +0.5 risk")
        if crisis_hub_qw > HUB_CRISIS_WEEKS:
            notes.append(f"HUB CAPACITY CRISIS: {crisis_hub} has only "
                          f"{hub.loc[crisis_hub].headroom:.0f} units/wk of real spare capacity; "
                          f"already-committed demand this scenario alone forces a "
                          f"{crisis_hub_qw}-week queue here -- this is a genuine infrastructure "
                          f"constraint (not a routing failure), escalate for a different hub or a "
                          f"capacity investment rather than treating the resulting lead time as real")
        if lead > shelf_life:
            notes.append(f"SHELF-LIFE RISK: EffLead ({int(lead)}d) exceeds this material's shelf "
                          f"life ({int(shelf_life)}d) by {int(lead-shelf_life)}d -- product may arrive "
                          f"degraded/expired, +1.5 risk, manual review required")
        if is_cross_family_fallback:
            notes.append("DISCLAIMER: no native lane existed for this MaterialFamily+scenario; "
                          "this lane's pricing is borrowed from a different material family on the "
                          "same real country pair (fresh compliance check on the actual hub, but the "
                          "cost/lead/risk numbers were never specifically quoted for this cargo) -- "
                          "not scored with any risk penalty, treat as an estimate needing manual costing")
        if r.RouteOptionID in primary_ids and r.RouteOptionID != own_primary_id:
            notes.append("used another shipment's primary lane")
        strict_solved = "No" if (waiver and hz == "Lithium Handling") else "Yes"
        rows.append(dict(ShipmentID=s.ShipmentID, Scenario=scen, Priority=m.PriorityClass,
                          Qty=s.Qty, RouteOptionID=r.RouteOptionID, FromHub=r.FromHub, ToHub=r.ToHub,
                          Mode=r.TransportMode, EffLead=lead, Cost=cost,
                          RiskAdj=round(risk, 2), CO2=float(r.CO2Kg),
                          BLead=b_lead, BCost=b_cost, BRisk=b_risk,
                          PriorityScore=round(score_priority(lead, cost, risk, m.PriorityClass), 4),
                          StrictComplianceSolved=strict_solved,
                          Solved="Yes", Notes="; ".join(notes)))

    return pd.DataFrame(rows)


def run_external_scenario(data, hub: pd.DataFrame, dead_hubs: set, scen: str) -> pd.DataFrame:
    """Mirrors legacy's External Shipments (cost/kg, A10/A11) body for ONE scenario."""
    ext, mat, ro = data.ext, data.mat, data.ro
    ints_by_id = data.ints_by_id
    hubs_by_stage_country, hubs_by_stage_city = data.hubs_by_stage_country, data.hubs_by_stage_city
    primary, primary_ids = data.primary, data.primary_ids
    cpk_min, cpk_max = data.cpk_min, data.cpk_max
    groups = data.cand_by_scen[scen]
    donor_cache: dict = {}

    work = ext.copy()
    work["prio"] = work.InternalShipmentID_Link.map(
        lambda sid: PRIO[mat.loc[ints_by_id.loc[sid].MaterialNo_Anon].PriorityClass])
    work = work.sort_values(["prio", "PUP_Date"])

    committed_e, committed_baseline_e, committed_hub_e = {}, {}, {}
    committed_parents_e, committed_baseline_hub_e = {}, {}
    ext_rows = []

    for _, e in work.iterrows():
        intl = ints_by_id.loc[e.InternalShipmentID_Link]
        m = mat.loc[intl.MaterialNo_Anon]
        hz = m.HazardClass if isinstance(m.HazardClass, str) else None
        cold = m.TempRequirement == "Cold Chain"
        shelf_life = m.ShelfLifeDays
        key = (e.MaterialFamily_Link, e.InternalStageFrom_Link, e.InternalStageTo_Link)
        try:
            cc = groups.get_group(key)
        except KeyError:
            cc = pd.DataFrame()

        own_primary_id = None
        try:
            p = primary.loc[(e.MaterialFamily_Link, e.InternalStageFrom_Link, e.InternalStageTo_Link,
                              intl.ShipFrom_Alias, intl.ShipTo_Alias)]
            if isinstance(p, pd.DataFrame):
                p = p.iloc[0]
            own_primary_id = p.RouteOptionID
            be_committed = committed_baseline_e.get(p.RouteOptionID, 0.0)
            be_hub_qw = combined_hub_qweeks(hub, intl.ShipFrom_Alias, intl.ShipTo_Alias, committed_baseline_hub_e)
            b_lead = eff_lead(p.BaseLeadTimeDays, intl.Qty, p.CapacityUnitsPerWeek, be_committed, be_hub_qw)
            committed_baseline_e[p.RouteOptionID] = be_committed + intl.Qty
            commit_hub_usage(intl.ShipFrom_Alias, intl.ShipTo_Alias, intl.Qty, committed_baseline_hub_e)
            b_cpk, b_risk = p.BaseCostEUR / e.ChargeableWeight_KG, float(p.RiskScore)
            if hub.loc[intl.ShipFrom_Alias].disrupted or hub.loc[intl.ShipTo_Alias].disrupted:
                b_risk += DISRUPT_PENALTY
            if not (hub_pass(hub, intl.ShipFrom_Alias, hz) and hub_pass(hub, intl.ShipTo_Alias, hz)):
                b_risk += HAZ_PENALTY
            if cold and not (hub.loc[intl.ShipFrom_Alias].ColdChainAvailable == "Yes"
                              and hub.loc[intl.ShipTo_Alias].ColdChainAvailable == "Yes"):
                b_risk += HAZ_PENALTY
            if b_lead > shelf_life:
                b_risk += SHELF_PENALTY
        except KeyError:
            b_lead = b_cpk = b_risk = np.nan

        best, best_key, is_cross_family_fallback = None, None, False

        def _filter_into_pools_e(candidates):
            ps, pw = [], []
            for r in candidates:
                if r.FromHub in dead_hubs or r.ToHub in dead_hubs:
                    continue
                cold_ok = (not cold) or (hub.loc[r.FromHub].ColdChainAvailable == "Yes"
                                          and hub.loc[r.ToHub].ColdChainAvailable == "Yes")
                if not cold_ok:
                    continue
                haz_ok = hub_pass(hub, r.FromHub, hz) and hub_pass(hub, r.ToHub, hz)
                (ps if haz_ok else pw).append(r)
            return ps, pw

        pool_strict, pool_waiver = _filter_into_pools_e([r for _, r in cc.iterrows()])
        if not pool_strict and not pool_waiver:
            cf_candidates = cross_family_candidates(
                hub, dead_hubs, hubs_by_stage_country, donor_cache, ro,
                e.InternalStageFrom_Link, e.InternalStageTo_Link, scen, hz, cold,
                hub.loc[intl.ShipFrom_Alias].Country, hub.loc[intl.ShipTo_Alias].Country)
            pool_strict, pool_waiver = _filter_into_pools_e(cf_candidates)
            is_cross_family_fallback = bool(pool_strict or pool_waiver)
        pool = pool_strict if pool_strict else pool_waiver
        waiver = not pool_strict and bool(pool_waiver)

        candidates_scored = []
        for r in pool:
            re_committed = committed_e.get(r.RouteOptionID, 0.0)
            hub_qw = combined_hub_qweeks(hub, r.FromHub, r.ToHub, committed_hub_e)
            lead = eff_lead(r.BaseLeadTimeDays, intl.Qty, r.CapacityUnitsPerWeek, re_committed, hub_qw)
            cpk = r.BaseCostEUR / e.ChargeableWeight_KG
            base_risk = float(r.RiskScore) + (HAZ_PENALTY if waiver else 0.0) \
                + (DISRUPT_PENALTY if (hub.loc[r.FromHub].disrupted or hub.loc[r.ToHub].disrupted) else 0.0)
            on_time = lead <= shelf_life
            risk = base_risk + (0.0 if on_time else SHELF_PENALTY)
            sc = score_cpk(lead, cpk, risk, cpk_min, cpk_max)
            candidates_scored.append((r, lead, cpk, base_risk, risk, sc, on_time))

        on_time_pool = [c for c in candidates_scored if c[6]]
        eval_pool = on_time_pool if on_time_pool else candidates_scored
        all_lead_capped = all(c[1] > L_MAX for c in eval_pool)
        all_risk_capped = all(c[4] > R_MAX for c in eval_pool)
        for r, lead, cpk, base_risk, risk, sc, on_time in eval_pool:
            if all_lead_capped:
                k = (lead, sc, cpk, risk)
            elif all_risk_capped:
                k = (risk, sc, cpk, lead)
            else:
                k = (sc, cpk, risk)
            if best is None or k < best_key:
                best, best_key = (r, lead, cpk, base_risk, risk), k

        if best is None:
            ext_rows.append(dict(DeliveryNo=e.DeliveryNo, InternalShipmentID=e.InternalShipmentID_Link,
                                  Scenario=scen, Priority=m.PriorityClass, ChargeableWeightKG=e.ChargeableWeight_KG,
                                  RouteOptionID="", FromHub="", ToHub="", Mode="",
                                  EffLead=None, CostPerKG=None, RiskAdj=None, CO2=None,
                                  BLead=b_lead, BCostPerKG=b_cpk, BRisk=b_risk, PriorityScore=None,
                                  StrictComplianceSolved="No",
                                  Solved="No", Notes="UNSOLVED — no compliant lane found (native or cross-family); escalate"))
            continue

        r, lead, cpk, base_risk, risk = best
        crisis_hub, crisis_hub_qw = None, 0
        for hh in (r.FromHub, r.ToHub):
            hh_qw = hub_qweeks(hub, hh, committed_hub_e)
            if hh_qw > crisis_hub_qw:
                crisis_hub, crisis_hub_qw = hh, hh_qw
        re_committed = committed_e.get(r.RouteOptionID, 0.0)
        single_cpk = cpk
        single_score = score_cpk(lead, single_cpk, risk, cpk_min, cpk_max)
        split_options = try_hub_split(hub, dead_hubs, hubs_by_stage_city, e.InternalStageFrom_Link,
                                       e.InternalStageTo_Link, r, intl.Qty, re_committed, hz, cold, committed_hub_e)
        best_opt = None
        for opt in split_options:
            opt_lead = float(r.BaseLeadTimeDays) + 7 * (opt["weeks"] - 1)
            opt_on_time = opt_lead <= shelf_life
            opt_risk = base_risk + (0.0 if opt_on_time else SHELF_PENALTY)
            opt_sib_qty = sum(sb["sibling_qty"] for sb in opt["siblings"])
            opt_extra_cost = sum(hub.loc[sb["sibling"]].FixedHandlingCost_EUR
                                  + hub.loc[sb["sibling"]].VariableHandlingCostPerUnit_EUR * sb["sibling_qty"]
                                  for sb in opt["siblings"])
            opt_cpk = (float(r.BaseCostEUR) + opt_extra_cost) / e.ChargeableWeight_KG
            opt_score = score_cpk(opt_lead, opt_cpk, opt_risk, cpk_min, cpk_max)
            if opt_score < single_score and (best_opt is None or opt_score < best_opt["score"]):
                best_opt = dict(split=opt, lead=opt_lead, risk=opt_risk, cpk=opt_cpk,
                                 sib_qty=opt_sib_qty, score=opt_score)
        use_split = best_opt is not None
        notes = []
        already_committed = e.InternalShipmentID_Link in committed_parents_e.get(r.RouteOptionID, set())
        if use_split:
            split, sib_qty = best_opt["split"], best_opt["sib_qty"]
            lead, cpk, risk = best_opt["lead"], best_opt["cpk"], best_opt["risk"]
            lane_qty = intl.Qty - sib_qty
            if not already_committed:
                committed_e[r.RouteOptionID] = re_committed + lane_qty
                commit_hub_usage(r.FromHub, r.ToHub, intl.Qty, committed_hub_e, split=split)
                committed_parents_e.setdefault(r.RouteOptionID, set()).add(e.InternalShipmentID_Link)
            n_sib = len(split["siblings"])
            sib_desc = "; ".join(f"{int(sb['sibling_qty'])}u via {sb['sibling']} ({sb['side']} side)"
                                  for sb in split["siblings"])
            split_note = (f"hub split ({n_sib}-way): {sib_desc} -- cuts to {split['weeks']} wk(s) "
                          f"from {split['weeks_single']} single-hub; downstream DCA consolidation effort "
                          f"not modeled, human review recommended" +
                          (f"; {n_sib} extra hubs used -- real coordination overhead scales with hub "
                           f"count (A24, bounded at {MAX_SPLIT_SIBLINGS}), weigh against the lead-time "
                           f"gain before approving" if n_sib > 1 else ""))
            if cpk > cpk_max and single_cpk > 0 and cpk / single_cpk >= COST_CLIP_DISCLOSE_RATIO:
                split_note += (f"; COST-CLIP CAUTION: real split cost/kg is "
                               f"{cpk/single_cpk:.1f}x the single-hub fee -- cost/kg normalizes "
                               f"the same past EUR{cpk_max:.2f}/kg regardless of magnitude, so the "
                               f"score cannot distinguish this from a smaller overage; verify the true "
                               f"euro tradeoff before approving")
            notes.append(split_note)
        else:
            cpk = single_cpk
            if not already_committed:
                committed_e[r.RouteOptionID] = re_committed + intl.Qty
                commit_hub_usage(r.FromHub, r.ToHub, intl.Qty, committed_hub_e)
                committed_parents_e.setdefault(r.RouteOptionID, set()).add(e.InternalShipmentID_Link)
            queue_weeks = queue_weeks_for(re_committed, r.CapacityUnitsPerWeek)
            if queue_weeks > 0:
                notes.append(f"capacity contention: queued {queue_weeks} wk(s) behind higher-priority demand")
            if math.ceil(intl.Qty / r.CapacityUnitsPerWeek) > 1:
                notes.append(f"multi-week split ({math.ceil(intl.Qty/r.CapacityUnitsPerWeek)} wks)")
        if crisis_hub_qw > HUB_CRISIS_WEEKS:
            notes.append(f"HUB CAPACITY CRISIS: {crisis_hub} has only "
                          f"{hub.loc[crisis_hub].headroom:.0f} units/wk of real spare capacity; "
                          f"already-committed demand this scenario alone forces a "
                          f"{crisis_hub_qw}-week queue here -- this is a genuine infrastructure "
                          f"constraint (not a routing failure), escalate for a different hub or a "
                          f"capacity investment rather than treating the resulting lead time as real")
        if lead > shelf_life:
            notes.append(f"SHELF-LIFE RISK: EffLead ({int(lead)}d) exceeds this material's shelf "
                          f"life ({int(shelf_life)}d) by {int(lead-shelf_life)}d -- product may arrive "
                          f"degraded/expired, +1.5 risk, manual review required")
        if already_committed:
            notes.append("same lot already committed capacity to this route via an earlier "
                          "last-mile leg (A17) -- not counted twice")
        if waiver:
            notes.append("hazard waiver +1.5 risk — manual review")
        if hub.loc[r.FromHub].disrupted or hub.loc[r.ToHub].disrupted:
            notes.append("disrupted hub +0.5 risk")
        if is_cross_family_fallback:
            notes.append("DISCLAIMER: no native lane existed for this MaterialFamily+scenario; "
                          "this lane's pricing is borrowed from a different material family on the "
                          "same real country pair (fresh compliance check on the actual hub, but the "
                          "cost/lead/risk numbers were never specifically quoted for this cargo) -- "
                          "not scored with any risk penalty, treat as an estimate needing manual costing")
        if r.RouteOptionID in primary_ids and r.RouteOptionID != own_primary_id:
            notes.append("used another shipment's primary lane")
        strict_solved = "No" if (waiver and hz == "Lithium Handling") else "Yes"
        ext_rows.append(dict(DeliveryNo=e.DeliveryNo, InternalShipmentID=e.InternalShipmentID_Link,
                              Scenario=scen, Priority=m.PriorityClass, ChargeableWeightKG=e.ChargeableWeight_KG,
                              RouteOptionID=r.RouteOptionID, FromHub=r.FromHub, ToHub=r.ToHub,
                              Mode=r.TransportMode, EffLead=lead, CostPerKG=round(float(cpk), 4),
                              RiskAdj=round(risk, 2), CO2=float(r.CO2Kg),
                              BLead=b_lead, BCostPerKG=b_cpk, BRisk=b_risk,
                              PriorityScore=round(score_cpk_priority(lead, cpk, risk, m.PriorityClass, cpk_min, cpk_max), 4),
                              StrictComplianceSolved=strict_solved,
                              Solved="Yes", Notes="; ".join(notes)))

    return pd.DataFrame(ext_rows)


def run_scenario_full(data, scen: str, hub_overrides: dict[str, dict] | None = None):
    """Top-level entry: builds a private hub frame for this one call (applying overrides if
    given), then runs both Internal and External passes. Never mutates `data` or any shared
    state -- safe to call concurrently for different scenarios/parameters/users."""
    hc = data.hc if not hub_overrides else apply_hub_overrides(data.hc, hub_overrides)
    hub, dead_hubs = set_hub_disruption_state(hc, scen)
    res = run_internal_scenario(data, hub, dead_hubs, scen)
    res_ext = run_external_scenario(data, hub, dead_hubs, scen)
    return res, res_ext
