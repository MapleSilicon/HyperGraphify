from __future__ import annotations

import stim

from hypergraphify import (
    HyperGraphTransformer,
    detect_hyperedges,
    TransformationVerifier,
)


def test_hyperedge_detection_and_verify():
    dem = stim.DetectorErrorModel()
    dem.append_error(
        0.1,
        [
            stim.DemTarget.relative_detector_id(0),
            stim.DemTarget.relative_detector_id(1),
            stim.DemTarget.relative_detector_id(2),
        ],
    )

    # hyper-edge detection
    hyperedges = detect_hyperedges(dem)
    assert len(hyperedges) == 1
    assert hyperedges[0].detector_ids == (0, 1, 2)

    transformer = HyperGraphTransformer()
    transformed = transformer.transform(dem)

    verifier = TransformationVerifier()
    results = verifier.verify(dem, transformed)
    assert results["valid"] is True
