from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any
import stim


@dataclass(frozen=True)
class HyperEdge:
    detector_ids: Tuple[int, ...]
    instruction_index: int
    probability: float
    raw: Any


def detect_hyperedges(dem: stim.DetectorErrorModel) -> List[HyperEdge]:
    out: List[HyperEdge] = []
    for idx, instr in enumerate(dem):
        if getattr(instr, "type", None) != "error":
            continue

        args = instr.args_copy() if hasattr(instr, "args_copy") else []
        p = float(args[0]) if args else 0.0

        dets: List[int] = []
        for t in instr.targets_copy():
            if hasattr(t, "is_relative_detector_id") and t.is_relative_detector_id():
                dets.append(int(t.val))
            elif isinstance(t, int):
                dets.append(int(t))

        if len(dets) >= 3:
            out.append(HyperEdge(tuple(dets), idx, p, instr))
    return out


class HyperGraphTransformer:
    def __init__(self):
        from .decomposer import HyperGraphifier
        self._HyperGraphifier = HyperGraphifier

    def transform(self, dem: stim.DetectorErrorModel) -> stim.DetectorErrorModel:
        hg = self._HyperGraphifier(dem)
        return hg.graphify(validate=True)


class TransformationVerifier:
    def verify(self, original: stim.DetectorErrorModel, transformed: stim.DetectorErrorModel) -> Dict[str, Any]:
        original_non_empty = str(original).strip() != ""
        transformed_non_empty = str(transformed).strip() != ""

        def is_graphlike_manual(d: stim.DetectorErrorModel) -> bool:
            for instr in d:
                if getattr(instr, "type", None) != "error":
                    continue
                dets = 0
                for t in instr.targets_copy():
                    if hasattr(t, "is_relative_detector_id") and t.is_relative_detector_id():
                        dets += 1
                    elif isinstance(t, int):
                        dets += 1
                if dets > 2:
                    return False
            return True

        valid = original_non_empty and transformed_non_empty and is_graphlike_manual(transformed)
        return {
            "original_non_empty": original_non_empty,
            "transformed_non_empty": transformed_non_empty,
            "valid": valid,
        }
