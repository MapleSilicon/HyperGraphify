"""
Comprehensive tests for HyperGraphify on simple synthetic DEMs.
"""

import os
import sys
import stim
import pymatching

# Local src/ package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hypergraphify import HyperGraphTransformer, TransformationVerifier


def is_graphlike_dem(dem: stim.DetectorErrorModel) -> bool:
    """Manual graphlike check for older Stim versions."""
    for instr in dem:
        if isinstance(instr, stim.DemInstruction) and instr.type == "error":
            det_count = 0
            for t in instr.targets_copy():
                if isinstance(t, stim.DemTarget) and t.is_relative_detector_id():
                    det_count += 1
            if det_count > 2:
                return False
    return True


def run_test(name: str, dem_text: str) -> bool:
    print("\n" + "=" * 60)
    print(f"Test: {name}")
    print("=" * 60)

    dem = stim.DetectorErrorModel(dem_text)

    print("Original DEM:")
    print(dem)
    print("Original is_graphlike (manual):", is_graphlike_dem(dem))

    transformer = HyperGraphTransformer(verbose=True)
    transformed = transformer.transform(dem)

    print("\nTransformed DEM:")
    print(transformed)
    print("Transformed is_graphlike (manual):", is_graphlike_dem(transformed))

    verifier = TransformationVerifier(verbose=True)
    results = verifier.verify(dem, transformed)
    print("\nVerification results:", results)

    changed = (str(dem) != str(transformed))
    print("DEM changed:", changed)

    # Try PyMatching on the transformed DEM
    try:
        matcher = pymatching.Matching.from_detector_error_model(transformed)
        print("\nPyMatching:")
        print(f"  num_nodes = {matcher.num_nodes}")
        print(f"  num_edges = {matcher.num_edges}")
        return True
    except Exception as e:
        print(f"\nPyMatching error: {e}")
        return False


def main():
    print("HyperGraphify Comprehensive Test Suite")

    test1 = run_test(
        "Simple 3-detector hyper-edge",
        """
error(0.1) D0 D1 D2
detector D0
detector D1
detector D2
logical_observable L0
"""
    )

    test2 = run_test(
        "Mixed hyper-edges and graphlike edges",
        """
error(0.1) D0 D1 D2
error(0.05) D3 D4
error(0.02) D5 D6 D7
detector D0
detector D1
detector D2
detector D3
detector D4
detector D5
detector D6
detector D7
logical_observable L0
"""
    )

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"Test 1: {'PASS' if test1 else 'FAIL'}")
    print(f"Test 2: {'PASS' if test2 else 'FAIL'}")


if __name__ == "__main__":
    main()
