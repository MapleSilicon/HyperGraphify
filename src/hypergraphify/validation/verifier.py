"""
Verifier module for validating transformations.

v0.1:
- Basic structural checks only.
- No full logical-equivalence proof yet.
"""

from __future__ import annotations

from typing import Dict

import stim

from hypergraphify.transform.decomposer import HyperGraphTransformer


class TransformationVerifier:
    """
    Verify that transformations at least produce structurally valid DEMs.

    Later:
    - logical observable preservation
    - error weight distribution checks
    - degeneracy analysis
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.verification_log = []

    def verify(
        self,
        original_dem: stim.DetectorErrorModel,
        transformed_dem: stim.DetectorErrorModel,
    ) -> Dict[str, bool]:
        """
        Perform basic validation.

        For v0.1:
        - both DEMs must be non-empty
        - both must be valid DetectorErrorModel instances
        """
        results = {
            "original_non_empty": self._has_instructions(original_dem),
            "transformed_non_empty": self._has_instructions(transformed_dem),
        }

        results["valid"] = all(results.values())

        self.verification_log.append(
            {
                "original_len": len(list(original_dem)),
                "transformed_len": len(list(transformed_dem)),
                "results": results,
            }
        )

        if self.verbose:
            print(f"[HyperGraphify] verification results: {results}")

        return results

    @staticmethod
    def _has_instructions(dem: stim.DetectorErrorModel) -> bool:
        return len(list(dem)) > 0

    def get_verification_log(self):
        return list(self.verification_log)
