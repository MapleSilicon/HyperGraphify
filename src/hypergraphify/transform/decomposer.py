"""
Decomposer: transform non-graphlike DEMs into graphlike ones.

Rules:
- We call any error with ≥3 detector targets a "hyper-edge".
- We decompose each hyper-edge into a chain of 2-detector errors.
- We introduce virtual detector IDs starting above the max existing D index.
"""

from typing import List, Dict, Any
import stim


class HyperGraphTransformer:
    """
    Transform non-graphlike detector error models into graphlike DEMs
    by decomposing hyper-edges into chains of 2-detector errors.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.transformation_log: List[Dict[str, Any]] = []

    # --- helpers ---------------------------------------------------------

    def _max_detector_id(self, dem: stim.DetectorErrorModel) -> int:
        max_id = -1
        for instr in dem:
            if isinstance(instr, stim.DemInstruction) and instr.type == "error":
                for t in instr.targets_copy():
                    if isinstance(t, stim.DemTarget) and t.is_relative_detector_id():
                        if t.val > max_id:
                            max_id = t.val
        return max_id

    def get_transformation_log(self) -> List[Dict[str, Any]]:
        return self.transformation_log

    # --- core API --------------------------------------------------------

    def transform(self, dem: stim.DetectorErrorModel) -> stim.DetectorErrorModel:
        """
        Transform DEM:
        - keep graphlike errors as-is
        - decompose hyper-edges into chains of 2-detector errors
        - keep non-error instructions as-is
        """
        max_det = self._max_detector_id(dem)
        next_virtual = max_det + 1

        lines: List[str] = []
        hyper_count = 0

        for idx, instr in enumerate(dem):
            if isinstance(instr, stim.DemInstruction) and instr.type == "error":
                args = instr.args_copy()
                prob = float(args[0]) if args else 0.0

                detectors: List[int] = []
                others = []  # logical obs etc.

                for t in instr.targets_copy():
                    if isinstance(t, stim.DemTarget) and t.is_relative_detector_id():
                        detectors.append(t.val)
                    else:
                        others.append(t)

                if len(detectors) >= 3:
                    # This is a hyper-edge
                    hyper_count += 1
                    if self.verbose:
                        print(f"[HyperGraphify] decomposing hyper-edge at instr {idx}: D{detectors}")

                    original_detectors = list(detectors)
                    edges = []

                    # naive chain: D0 - V0 - D1 - V1 - D2 - ...
                    # for n detectors, we make (2*(n-1)) edges
                    for i in range(len(detectors) - 1):
                        v = next_virtual
                        next_virtual += 1

                        a = detectors[i]
                        text_a = f"D{a}"
                        text_b = f"D{v}"
                        edges.append((text_a, text_b))

                        text_a = f"D{v}"
                        b = detectors[i + 1]
                        text_b = f"D{b}"
                        edges.append((text_a, text_b))

                    # log
                    self.transformation_log.append(
                        {
                            "type": "hyperedge_decomposed",
                            "version": "0.1.0",
                            "instruction_index": idx,
                            "original_detectors": original_detectors,
                            "virtual_nodes": list(range(max_det + 1, next_virtual)),
                            "edges_created": len(edges),
                            "probability": prob,
                        }
                    )

                    # emit new graphlike edges
                    # (for now, keep same prob on each edge – correctness work later)
                    for (d1, d2) in edges:
                        lines.append(f"error({prob}) {d1} {d2}")

                    # we **do not** re-emit the original hyper-edge
                    continue

                else:
                    # already graphlike (0–2 detectors) => keep original text
                    lines.append(str(instr))

            else:
                # Non-error instructions: detector, logical_observable, shift_detectors, etc.
                lines.append(str(instr))

        if self.verbose:
            print(f"[HyperGraphify] total hyper-edges decomposed: {hyper_count}")

        dem_str = "\n".join(lines)
        return stim.DetectorErrorModel(dem_str)
