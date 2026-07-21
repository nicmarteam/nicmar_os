from typing import List, Protocol, runtime_checkable
from src.context.models import ContextRequest, ContextFragment

@runtime_checkable
class ContextProvider(Protocol):
    name: str
    priority: int

    async def provide(self, request: ContextRequest) -> List[ContextFragment]:
        """
        Furnizează o listă de fragmente de context pe baza cererii primite.
        Fiecare fragment are asociat un număr de tokeni și o prioritate.
        """
        ...
