import stim
import pymatching
from hypergraphify import HyperGraphTransformer

def test_transform_output_is_pymatching_compatible():
    dem = stim.DetectorErrorModel("""
        error(0.1) D0 D1 D2
        error(0.05) D3 D4
        detector D0
        detector D1
        detector D2
        detector D3
        detector D4
        logical_observable L0
    """.strip())

    t = HyperGraphTransformer()
    out = t.transform(dem)

    # must not contain any 3+ detector errors
    for instr in out:
        if instr.type != "error":
            continue
        dets = 0
        for tar in instr.targets_copy():
            if tar.is_relative_detector_id():
                dets += 1
        assert dets <= 2

    # must load into pymatching
    m = pymatching.Matching(out)
    assert m.num_edges > 0
