from abc import ABC, abstractmethod
from typing import Any

class RouteAlgorithm(ABC):
    @abstractmethod
    async def compute_route(self, request: Any) -> Any:
        ...
