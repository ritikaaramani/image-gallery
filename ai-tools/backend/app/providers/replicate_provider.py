# backend/app/providers/replicate_provider.py
import os
import requests
from typing import List, Dict, Any, Union
from .base import ProviderInterface

# Optional: use replicate SDK if installed; fallback to HTTP if not
try:
    import replicate
    _HAS_SDK = True
except Exception:
    _HAS_SDK = False

class ReplicateProvider(ProviderInterface):
    name = "replicate"

    def __init__(self, api_token: Union[str, None] = None, model_version: Union[str, None] = None):
        token = api_token or os.getenv("REPLICATE_API_TOKEN")
        if not token:
            raise RuntimeError("REPLICATE_API_TOKEN not set in environment or constructor")

        self.model_version = model_version or os.getenv("REPLICATE_MODEL_VERSION")
        if not self.model_version:
            raise RuntimeError("REPLICATE_MODEL_VERSION not set in environment or constructor")

        self.api_token = token

        # If SDK available, create client instance for convenience
        if _HAS_SDK:
            self.client = replicate.Client(api_token=token)
        else:
            self.client = None
            self._predictions_url = "https://api.replicate.com/v1/predictions"

    def generate(self, prompt: str, seed: Union[int, None], width: int, height: int, steps: int, batch: int, extra: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Returns list of {"bytes": ..., "mime": "image/png", "meta": {...}}
        Uses replicate SDK if available (blocking), else uses HTTP Predictions API with Prefer: wait=60.
        """
        input_payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_inference_steps": steps
        }
        # include extra params if present (guidance_scale, negative_prompt, etc.)
        if extra:
            for k, v in extra.items():
                # don't override built-ins inadvertently
                if k not in input_payload:
                    input_payload[k] = v

        if seed is not None:
            input_payload["seed"] = int(seed)

        out = []

        if self.client:
            # SDK path (blocking convenience)
            results = self.client.run(self.model_version, input=input_payload)
            # results is often a list of URLs; handle accordingly
            for item in results or []:
                if isinstance(item, str) and item.startswith("http"):
                    r = requests.get(item, timeout=60)
                    r.raise_for_status()
                    out.append({"bytes": r.content, "mime": r.headers.get("Content-Type", "image/png"), "meta": {"provider_job": None}})
                else:
                    # try to treat as bytes or file-like
                    try:
                        b = item.read()
                        out.append({"bytes": b, "mime": "image/png", "meta": {}})
                    except Exception:
                        out.append({"bytes": str(item).encode(), "mime": "text/plain", "meta": {}})
            return out

        # HTTP fallback path
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
            "Prefer": "wait=60"  # wait up to 60 seconds for job to finish synchronously
        }
        payload = {
            "version": self.model_version,
            "input": input_payload
        }
        resp = requests.post(self._predictions_url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        job = resp.json()

        # job may include 'output' which can be list of urls or base64 strings
        for item in job.get("output", []) or []:
            if isinstance(item, str) and item.startswith("http"):
                r = requests.get(item, timeout=60)
                r.raise_for_status()
                out.append({"bytes": r.content, "mime": r.headers.get("Content-Type", "image/png"), "meta": {"provider_job": job.get("id")}})
            else:
                # attempt base64 decode; if fails, store as text bytes
                import base64
                try:
                    b = base64.b64decode(item)
                    out.append({"bytes": b, "mime": "image/png", "meta": {"provider_job": job.get("id")}})
                except Exception:
                    out.append({"bytes": str(item).encode(), "mime": "text/plain", "meta": {"provider_job": job.get("id")}})
        return out

    def abort(self, job_identifier: str) -> bool:
        # Replicate public API has no reliable abort for predictions; return False.
        return False