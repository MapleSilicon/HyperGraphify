import stim
from hypergraphify import HyperGraphTransformer

def count_hyperedges(dem: stim.DetectorErrorModel) -> int:
    c = 0
    for instr in dem:
        if instr.type != "error":
            continue
        dets = 0
        for t in instr.targets_copy():
            if t.is_relative_detector_id():
                dets += 1
        if dets >= 3:
            c += 1
    return c

def test_transform_removes_all_hyperedges():
    dem = stim.DetectorErrorModel("""
        error(0.1) D0 D1 D2
        error(0.02) D5 D6 D7
        error(0.05) D3 D4
    """.strip())

    t = HyperGraphTransformer()
    out = t.transform(dem)

    assert count_hyperedges(dem) == 2
    assert count_hyperedges(out) == 0
