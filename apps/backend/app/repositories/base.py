from typing import Generic, Protocol, TypeVar
T=TypeVar("T")
class Repository(Protocol,Generic[T]):
    """Persistence boundary; add domain repositories after keys are confirmed."""
    def list(self)->list[T]: ...
