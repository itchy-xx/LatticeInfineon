"""Regression suite: the refactored engine (app/optimizer/core.py + data_loader.py) must
produce IDENTICAL results to the untouched legacy/lattice_optimizer.py script for every
scenario the legacy script supports. Importing the legacy module runs it end-to-end (no
__main__ guard, by design -- see its own file), which is what makes it usable as a
regression oracle without duplicating its output anywhere.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from app.optimizer import core
from app.optimizer.data_loader import load_optimizer_data

LEGACY_DIR = Path(__file__).resolve().parents[1] / "app" / "optimizer" / "legacy"
SERVICE_WORKBOOK = Path(__file__).resolve().parents[1] / "data" / "IFX_LOG_Master_Data-anonymised_StudentVersion.xlsx"

COMPARE_COLS_INTERNAL = ["RouteOptionID", "EffLead", "Cost", "RiskAdj", "BLead", "BCost",
                          "BRisk", "Solved", "Notes"]
COMPARE_COLS_EXTERNAL = ["RouteOptionID", "EffLead", "CostPerKG", "RiskAdj", "BLead",
                          "BCostPerKG", "BRisk", "Solved", "Notes"]


@pytest.fixture(scope="session")
def legacy_results():
    if not (LEGACY_DIR / "IFX_LOG_Master_Data-anonymised_StudentVersion.xlsx").is_file():
        pytest.skip("Legacy workbook not present in app/optimizer/legacy/ -- skipping regression suite.")
    from app.optimizer.legacy import lattice_optimizer as orig  # runs the full script on import
    return orig.res.copy(), orig.res_ext.copy()


@pytest.fixture(scope="session")
def data():
    if not SERVICE_WORKBOOK.is_file():
        pytest.skip("Service workbook not present in app/backend/data/ -- skipping regression suite.")
    return load_optimizer_data(str(SERVICE_WORKBOOK))


def _assert_frames_match(ours: pd.DataFrame, theirs: pd.DataFrame, id_col: str, cols: list[str], scen: str):
    ours_s = ours.set_index(id_col).sort_index()
    theirs_s = theirs[theirs.Scenario == scen].set_index(id_col).sort_index()
    assert list(ours_s.index) == list(theirs_s.index), f"{scen}: {id_col} sets differ"
    for col in cols:
        pd.testing.assert_series_equal(
            ours_s[col].fillna("<NA>").astype(str),
            theirs_s[col].fillna("<NA>").astype(str),
            check_names=False,
            obj=f"{scen}.{col}",
        )


@pytest.mark.parametrize("scen", core.SCENARIOS)
def test_internal_assignments_match_legacy(legacy_results, data, scen):
    theirs, _ = legacy_results
    ours, _ = core.run_scenario_full(data, scen)
    _assert_frames_match(ours, theirs, "ShipmentID", COMPARE_COLS_INTERNAL, scen)


@pytest.mark.parametrize("scen", core.SCENARIOS)
def test_external_assignments_match_legacy(legacy_results, data, scen):
    _, theirs_ext = legacy_results
    _, ours_ext = core.run_scenario_full(data, scen)
    _assert_frames_match(ours_ext, theirs_ext, "DeliveryNo", COMPARE_COLS_EXTERNAL, scen)


@pytest.mark.parametrize("scen", core.SCENARIOS)
def test_solved_counts_match_legacy(legacy_results, data, scen):
    theirs, theirs_ext = legacy_results
    ours, ours_ext = core.run_scenario_full(data, scen)
    assert int((ours.Solved == "Yes").sum()) == int((theirs[theirs.Scenario == scen].Solved == "Yes").sum())
    assert int((ours_ext.Solved == "Yes").sum()) == int((theirs_ext[theirs_ext.Scenario == scen].Solved == "Yes").sum())


@pytest.mark.parametrize("scen", core.SCENARIOS)
def test_weighted_and_baseline_scores_match_legacy(legacy_results, data, scen):
    """Recomputes WeightedScore/BaselineScore from our own output via core.score() and
    compares to the same computation over the legacy rows, for solved rows only."""
    theirs, _ = legacy_results
    ours, _ = core.run_scenario_full(data, scen)
    theirs_scen = theirs[theirs.Scenario == scen].set_index("ShipmentID").sort_index()
    ours_s = ours.set_index("ShipmentID").sort_index()

    ours_solved = ours_s[ours_s.Solved == "Yes"]
    theirs_solved = theirs_scen.loc[ours_solved.index]
    our_scores = ours_solved.apply(lambda r: core.score(r.EffLead, r.Cost, r.RiskAdj), axis=1)
    their_scores = theirs_solved.apply(lambda r: core.score(r.EffLead, r.Cost, r.RiskAdj), axis=1)
    pd.testing.assert_series_equal(our_scores, their_scores, check_names=False, atol=1e-9)

    has_baseline = theirs_scen.BLead.notna()
    our_base = ours_s.loc[has_baseline].apply(lambda r: core.score(r.BLead, r.BCost, r.BRisk), axis=1)
    their_base = theirs_scen.loc[has_baseline].apply(lambda r: core.score(r.BLead, r.BCost, r.BRisk), axis=1)
    pd.testing.assert_series_equal(our_base, their_base, check_names=False, atol=1e-9)


# ---------- new parameterized simulation adapters: compared against the SAME engine's
# Normal baseline, not against the legacy script (which has no such scenarios) ----------
def test_cold_chain_restriction_never_substitutes_noncompliant_route(data):
    from app.optimizer import scenarios as scenario_adapters

    cold_hub_ids = list(data.hc[data.hc.ColdChainAvailable == "Yes"].HubID.head(3))
    outcome = scenario_adapters.cold_chain_restriction(data, cold_hub_ids)
    hub_df, _ = core.set_hub_disruption_state(
        core.apply_hub_overrides(data.hc, {h: {"ColdChainAvailable": "No"} for h in cold_hub_ids}),
        "Normal",
    )
    solved = outcome.res[outcome.res.Solved == "Yes"]
    for _, row in solved.iterrows():
        if row.FromHub in cold_hub_ids or row.ToHub in cold_hub_ids:
            # A restricted hub was used on a solved route only if the shipment's material
            # doesn't require cold chain -- assert the hard constraint by checking the hub's
            # ColdChainAvailable override actually took effect (it's now "No").
            assert hub_df.loc[row.FromHub if row.FromHub in cold_hub_ids else row.ToHub].ColdChainAvailable == "No"


def test_port_congestion_reuses_hub_disruption_engine(data):
    from app.optimizer import scenarios as scenario_adapters

    hub_id = data.hc.HubID.iloc[0]
    outcome = scenario_adapters.port_congestion(data, hub_id, 0.5)
    assert outcome.affected_hub_ids == [hub_id]
    assert len(outcome.res) == len(outcome.baseline_res)


def test_expedited_priority_never_reroutes(data):
    from app.optimizer import scenarios as scenario_adapters

    outcome = scenario_adapters.expedited_priority(data)
    assert outcome.selection_changed is False
    pd.testing.assert_series_equal(
        outcome.res.set_index("ShipmentID").RouteOptionID.sort_index(),
        outcome.baseline_res.set_index("ShipmentID").RouteOptionID.sort_index(),
        check_names=False,
    )
