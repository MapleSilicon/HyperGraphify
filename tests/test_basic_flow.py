import stim

from hypergraphify import (
    HyperGraphTransformer,
    detect_hyperedges,
    TransformationVerifier,
)

def test_hyperedge_detection_and_verify():
    dem = stim.DetectorErrorModel("""
        error(0.1) D0 D1 D2
        detector D0
        detector D1
        detector D2
        logical_observable L0
    """.strip())

    hyperedges = detect_hyperedges(dem)
    assert len(hyperedges) == 1
    assert hyperedges[0].detector_ids == (0, 1, 2)

    transformer = HyperGraphTransformer()
    transformed = transformer.transform(dem)

    verifier = TransformationVerifier()
    results = verifier.verify(dem, transformed)
    assert results["valid"] is True
