from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from portfolio_homepage.crew import PortfolioHomepageCrew


def _normalize_inputs(payload: Any) -> Dict[str, Any]:
    # AMP /kickoff payload is documented as {"inputs": {...}}
    if isinstance(payload, dict) and "inputs" in payload and isinstance(payload["inputs"], dict):
        payload = payload["inputs"]

    if payload is None:
        # Fallback: allow passing inputs through an env var if the runner uses it
        env = os.getenv("CREWAI_INPUTS") or os.getenv("INPUTS")
        if env:
            try:
                payload = json.loads(env)
            except Exception:
                payload = {"source_text": env}
        else:
            payload = {}

    if not isinstance(payload, dict):
        raise TypeError("Inputs must be a dict or a JSON object with key 'inputs'.")

    if "source_text" not in payload or not isinstance(payload["source_text"], str) or not payload["source_text"].strip():
        raise ValueError("Missing required input: source_text (non-empty string).")

    return payload


def run(inputs: Optional[Dict[str, Any]] = None, **kwargs: Any):
    # Some runners pass inputs via kwargs
    if inputs is None and kwargs:
        inputs = kwargs.get("inputs") or kwargs  # type: ignore[assignment]

    normalized = _normalize_inputs(inputs)
    result = PortfolioHomepageCrew().crew().kickoff(inputs=normalized)
    return result


if __name__ == "__main__":
    # Local smoke-test (requires OPENAI_API_KEY)
    sample = {"source_text": "T-shaped lead designer. Worked on data-heavy products."}
    run(sample)
