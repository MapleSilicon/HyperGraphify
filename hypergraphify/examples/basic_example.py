"""
Basic example of using HyperGraphify to transform a non-graphlike DEM.
"""

import stim
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import hypergraphify
import pymatching

def main():
    # Create a simple non-graphlike DEM
    dem = stim.DetectorErrorModel()
    dem.append("error", parens_arguments=[0.1], targets=[
        stim.DemTarget.relative_detector_id(0),
        stim.DemTarget.relative_detector_id(1),
        stim.DemTarget.relative_detector_id(2)
    ])
    dem.append("error", parens_arguments=[0.05], targets=[
        stim.DemTarget.relative_detector_id(3),
        stim.DemTarget.relative_detector_id(4)
    ])

    print("Original DEM:")
    print(dem)
    print(f"Original DEM is graphlike? {dem.is_graphlike}")

    # Transform the DEM to be graphlike
    transformer = hypergraphify.HyperGraphTransformer(verbose=True)
    graphlike_dem = transformer.transform(dem)

    print("\nTransformed DEM:")
    print(graphlike_dem)
    print(f"Transformed DEM is graphlike? {graphlike_dem.is_graphlike}")

    # Verify the transformation
    verifier = hypergraphify.TransformationVerifier(verbose=True)
    results = verifier.verify(dem, graphlike_dem)
    print("\nVerification results:", results)

    # Use the transformed DEM with PyMatching
    try:
        matcher = pymatching.Matching.from_detector_error_model(graphlike_dem)
        print("\nSuccessfully created PyMatching object from transformed DEM")
        print(f"Number of nodes in matching graph: {matcher.num_nodes}")
        print(f"Number of edges in matching graph: {matcher.num_edges}")
    except Exception as e:
        print(f"\nError creating PyMatching object: {e}")

    # Print transformation log
    print("\nTransformation log:")
    for log_entry in transformer.get_transformation_log():
        print(log_entry)

if __name__ == "__main__":
    main()