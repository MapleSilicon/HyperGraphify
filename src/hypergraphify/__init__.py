"""
Public API for HyperGraphify.

We expose:
- HyperGraphTransformer: core DEM transformer
- TransformationVerifier: basic structural verifier
"""

from .transform.decomposer import HyperGraphTransformer
from .validation.verifier import TransformationVerifier

# Backwards-compat alias if any old code tries to use HyperGraphifier
HyperGraphifier = HyperGraphTransformer

__all__ = [
    "HyperGraphTransformer",
    "HyperGraphifier",
    "TransformationVerifier",
]
