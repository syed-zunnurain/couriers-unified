from abc import ABC, abstractmethod
from typing import Dict, Any


class CancellableCourierInterface(ABC):
    @abstractmethod
    def cancel_shipment(self, courier_external_id: str) -> Dict[str, Any]:
        pass
