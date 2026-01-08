"""
Basic example of using HyperGraphify to transform a non-graphlike DEM.
"""

import os
import sys
import stim
import pymatching

# Use local src/ package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from hypergraphify import HyperGraphTransformer, TransformationVerifier


def is_graphlike_dem(dem: stim.DetectorErrorModel) -> bool:
    """
    Manual graphlike check for older Stim versions (no .is_graphlike).

    A DEM is graphlike if every error touches at most 2 detectors.
    """
    for instr in dem:
        if isinstance(instr, stim.DemInstruction) and instr.type == "error":
            det_count = 0
            for t in instr.targets_copy():
                if isinstance(t, stim.DemTarget) and t.is_relative_detector_id():
                    det_count += 1
            if det_count > 2:
                return False
    return True


def main():
    # Build DEM from text
    dem_text = """
error(0.1) D0 D1 D2
error(0.05) D3 D4
"""
    dem = stim.DetectorErrorModel(dem_text)

    print("Original DEM:")
    print(dem)
    print("Original is_graphlike (manual):", is_graphlike_dem(dem))

    transformer = HyperGraphTransformer(verbose=True)
    transformed_dem = transformer.transform(dem)

    print("\nTransformed DEM:")
    print(transformed_dem)
    print("Transformed is_graphlike (manual):", is_graphlike_dem(transformed_dem))

    verifier = TransformationVerifier(verbose=True)
    results = verifier.verify(dem, transformed_dem)
    print("\nVerification results:", results)

    # Use the transformed DEM with PyMatching
    try:
        matcher = pymatching.Matching.from_detector_error_model(transformed_dem)
        print("\nTransformed DEM is PyMatching-compatible")
        print(f"Number of nodes in matching graph: {matcher.num_nodes}")
        print(f"Number of edges in matching graph: {matcher.num_edges}")
    except Exception as e:
        print(f"\nError creating PyMatching object: {e}")

    print("\nTransformation log:")
    for entry in transformer.get_transformation_log():
        print(entry)


if __name__ == "__main__":
    main()
