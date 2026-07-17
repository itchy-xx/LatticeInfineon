from dataclasses import dataclass,field
@dataclass(frozen=True)
class FieldMapping:
    """External-to-canonical mapping; keep source columns out of domain code."""
    source_to_canonical:dict[str,str]=field(default_factory=dict)
    def apply(self,columns:list[str])->dict[str,str]:
        unknown=set(self.source_to_canonical)-set(columns)
        if unknown: raise ValueError(f"Configured source fields not found: {sorted(unknown)}")
        return self.source_to_canonical
