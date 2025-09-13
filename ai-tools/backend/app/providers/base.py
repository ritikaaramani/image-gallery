# backend/app/providers/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ProviderInterface(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str, width: int, height: int, steps: int, batch: int, extra: Dict[str,Any], seed: Optional[int] = None) -> List[Dict]:
        """Return list of artifacts: {bytes, mime, meta}"""
        raise NotImplementedError()

    @abstractmethod
    def abort(self, job_identifier: str) -> bool:
        """Attempt to abort a job (optional)"""
        raise NotImplementedError()