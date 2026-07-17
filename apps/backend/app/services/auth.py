from dataclasses import dataclass
@dataclass(frozen=True)
class Principal:
    subject: str
    roles: tuple[str,...]
def require_permission(_permission: str):
    """Placeholder; integrate the approved identity provider later."""
    def dependency()->Principal: return Principal("local-developer",("viewer",))
    return dependency
