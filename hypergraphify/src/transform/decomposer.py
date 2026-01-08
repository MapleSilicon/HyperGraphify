"""
Decomposer module for transforming non-graphlike detector error models into graphlike structures.
"""

import stim
import numpy as np
import networkx as nx
from typing import List, Dict, Tuple, Optional, Set


class HyperGraphTransformer:
    """
    Transform non-graphlike detector error models into graphlike structures
    by decomposing hyper-edges into chains of virtual nodes.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the transformer.
        
        Args:
            verbose: Whether to print detailed transformation information
        """
        self.verbose = verbose
        self.transformation_log = []
        self.next_virtual_id = 10000  # Start virtual IDs at a high number
        
    def transform(self, dem: stim.DetectorErrorModel) -> stim.DetectorErrorModel:
        """
        Transform a detector error model to be graphlike.
        
        Args:
            dem: Input detector error model with potential hyper-edges
            
        Returns:
            Transformed detector error model with graphlike structure
        """
        # Create a new DEM for the transformed model
        transformed_dem = stim.DetectorErrorModel()
        
        # Process each instruction in the DEM
        for i, instruction in enumerate(dem):
            if isinstance(instruction, stim.DemInstruction):
                if instruction.type == "error":
                    # Check if this is a hyper-edge (3+ detectors)
                    detectors = []
                    for target in instruction.targets_copy():
                        if target.is_relative_detector_id():
                            detectors.append(target.val)
                    
                    if len(detectors) >= 3:
                        # This is a hyper-edge, attempt decomposition
                        if self.verbose:
                            print(f"[HyperGraphify] Processing hyper-edge with detectors {detectors}")
                        
                        # Log the hyper-edge detection
                        self.transformation_log.append({
                            "type": "hyperedge_detected",
                            "instruction_index": i,
                            "detectors": tuple(detectors)
                        })
                        
                        # Attempt decomposition
                        chain_edges = self._decompose_hyperedge(
                            detectors, 
                            instruction.args_copy()
                        )
                        
                        if chain_edges:
                            # Add the decomposed edges to the transformed DEM
                            for edge in chain_edges:
                                targets = []
                                for t in edge["targets"]:
                                    targets.append(stim.DemTarget.relative_detector_id(t))
                                
                                if self.verbose:
                                    print(f"[HyperGraphify] Adding edge with targets {targets} and probability {edge['args'][0]}")
                                
                                transformed_dem.append(
                                    instruction_type="error",
                                    parens_arguments=edge["args"],
                                    targets=targets
                                )
                            
                            # Log the transformation
                            self.transformation_log.append({
                                "type": "hyperedge_decomposition",
                                "instruction_index": i,
                                "original_detectors": detectors,
                                "num_edges": len(chain_edges),
                                "virtual_nodes": len(chain_edges) - 1
                            })
                            
                            if self.verbose:
                                print(f"[HyperGraphify] Decomposed hyper-edge with {len(detectors)} detectors into {len(chain_edges)} edges")
                        else:
                            # Decomposition failed, keep original
                            if self.verbose:
                                print(f"[HyperGraphify] Failed to decompose hyper-edge with {len(detectors)} detectors, keeping original")
                            
                            transformed_dem.append(
                                instruction_type="error",
                                parens_arguments=instruction.args_copy(),
                                targets=instruction.targets_copy()
                            )
                    else:
                        # This is already graphlike, keep as is
                        transformed_dem.append(
                            instruction_type="error",
                            parens_arguments=instruction.args_copy(),
                            targets=instruction.targets_copy()
                        )
                else:
                    # Non-error instruction, keep as is
                    transformed_dem.append(
                        instruction_type=instruction.type,
                        parens_arguments=instruction.args_copy(),
                        targets=instruction.targets_copy()
                    )
        
        return transformed_dem
    
    def _decompose_hyperedge(self, detectors: List[int], args: List[float]) -> Optional[List[Dict]]:
        """
        Decompose a hyper-edge into a chain of graphlike edges.
        
        Args:
            detectors: List of detector IDs in the hyper-edge
            args: List of arguments (including error probability)
            
        Returns:
            List of graphlike edges or None if decomposition is not possible
        """
        if len(detectors) < 3:
            return None
            
        # Extract error probability
        error_prob = args[0] if args else 0.1
        
        # Calculate weight-preserving probability for each edge in the chain
        # For a weight-3 hyper-edge with probability p, we want to find p_i such that:
        # 1 - (1 - 2p) = 1 - (1 - 2p_i)^2
        # Solving for p_i: p_i = 0.5 * (1 - sqrt(1 - 2p))
        if len(detectors) == 3:
            edge_prob = 0.5 * (1 - np.sqrt(1 - 2 * error_prob))
        else:
            # For longer chains, use a simpler approximation
            edge_prob = error_prob / (len(detectors) - 1)
        
        # Create a chain of edges
        edges = []
        virtual_nodes = []
        
        # Create virtual nodes for the chain
        for i in range(len(detectors) - 2):
            virtual_id = self.next_virtual_id
            virtual_nodes.append(virtual_id)
            self.next_virtual_id += 1
        
        # First edge: first detector to first virtual node
        edges.append({
            "targets": [detectors[0], virtual_nodes[0]],
            "args": [edge_prob]
        })
        
        # Middle edges: virtual nodes to next detector
        for i in range(1, len(detectors) - 1):
            if i < len(detectors) - 2:
                # Virtual to virtual
                edges.append({
                    "targets": [virtual_nodes[i-1], virtual_nodes[i]],
                    "args": [edge_prob]
                })
            else:
                # Last virtual to last detector
                edges.append({
                    "targets": [virtual_nodes[i-1], detectors[-1]],
                    "args": [edge_prob]
                })
        
        return edges
    
    def get_transformation_log(self) -> List[Dict]:
        """
        Get the log of transformations performed.
        
        Returns:
            List of transformation records
        """
        return self.transformation_log