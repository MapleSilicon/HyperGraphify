"""
Core decomposition engine for transforming LDPC hyper-edges into graphlike chains.
"""

from typing import List, Tuple, Optional, Dict
import stim
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DecompositionResult:
    """Results of hyper-edge decomposition attempt."""
    success: bool
    original_detectors: List[int]
    transformed_edges: List[Tuple[int, int]]
    virtual_nodes: List[int]
    probability: float
    failure_reason: Optional[str] = None

class HyperGraphifier:
    """Main class for hyper-edge detection and decomposition."""
    
    def __init__(self, dem: stim.DetectorErrorModel):
        self.dem = dem
        self.detector_count = self._count_detectors()
        self.next_virtual_node = self.detector_count
        self.transformation_log = []
        
    def _count_detectors(self) -> int:
        """Count total detectors in DEM."""
        count = 0
        for instr in self.dem:
            for target in instr.targets_copy():
                if isinstance(target, stim.DemTarget) and target.is_relative_detector_id():
                    count = max(count, target.val + 1)
        return count
    
    def find_hyper_edges(self) -> List[Dict]:
        """Identify all hyper-edges (≥3 detectors) in DEM."""
        hyper_edges = []
        
        for idx, instruction in enumerate(self.dem):
            if instruction.type == "error":
                detectors = []
                probability = 0.0
                
                # Parse instruction
                args = instruction.args_copy()
                if args:
                    probability = float(args[0])
                
                # Get all detector targets
                for target in instruction.targets_copy():
                    if isinstance(target, stim.DemTarget):
                        if target.is_relative_detector_id():
                            detectors.append(target.val)
                
                if len(detectors) >= 3:
                    hyper_edges.append({
                        'detectors': detectors,
                        'probability': probability,
                        'instruction_index': idx,
                        'instruction': instruction
                    })
        
        return hyper_edges
    
    def decompose_hyper_edge(self, detectors: List[int], 
                           probability: float) -> DecompositionResult:
        """Decompose hyper-edge into chain of graphlike edges."""
        if len(detectors) < 3:
            return DecompositionResult(
                success=False,
                original_detectors=detectors,
                transformed_edges=[],
                virtual_nodes=[],
                probability=probability,
                failure_reason="Not a hyper-edge (<3 detectors)"
            )
        
        # Create chain decomposition
        virtual_nodes = []
        transformed_edges = []
        
        for i in range(len(detectors) - 1):
            virtual_node = self.next_virtual_node
            self.next_virtual_node += 1
            virtual_nodes.append(virtual_node)
            
            # Create edges: detector_i -> virtual -> detector_{i+1}
            transformed_edges.append((detectors[i], virtual_node))
            transformed_edges.append((virtual_node, detectors[i+1]))
        
        return DecompositionResult(
            success=True,
            original_detectors=detectors,
            transformed_edges=transformed_edges,
            virtual_nodes=virtual_nodes,
            probability=probability
        )
    
    def graphify(self, validate: bool = True) -> stim.DetectorErrorModel:
        """Convert DEM with hyper-edges to graphlike form."""
        # Find all hyper-edges
        hyper_edges = self.find_hyper_edges()
        
        if not hyper_edges:
            logger.info("No hyper-edges found. DEM is already graphlike.")
            return self.dem
        
        logger.info(f"Found {len(hyper_edges)} hyper-edges")
        
        # Track which instructions are hyper-edges
        hyper_edge_indices = {edge['instruction_index'] for edge in hyper_edges}
        
        # Create a new DEM
        new_dem = stim.DetectorErrorModel()
        
        for idx, instruction in enumerate(self.dem):
            if instruction.type == "error":
                if idx in hyper_edge_indices:
                    # This is a hyper-edge - decompose it
                    edge_info = next(e for e in hyper_edges if e['instruction_index'] == idx)
                    result = self.decompose_hyper_edge(
                        edge_info['detectors'],
                        edge_info['probability']
                    )
                    
                    if result.success:
                        # Add decomposed edges
                        edge_prob = result.probability / len(result.transformed_edges)
                        for a, b in result.transformed_edges:
                            new_dem.append(
                                "error",
                                [edge_prob],
                                [stim.DemTarget.relative_detector_id(a), 
                                 stim.DemTarget.relative_detector_id(b)]
                            )
                        
                        # Log the transformation
                        self.transformation_log.append({
                            'type': 'hyperedge_decomposed',
                            'original_detectors': result.original_detectors,
                            'virtual_nodes': result.virtual_nodes,
                            'edges_created': len(result.transformed_edges)
                        })
                    else:
                        # Keep original if decomposition failed
                        new_dem.append(instruction)
                        logger.warning(f"Failed to decompose hyper-edge at index {idx}: {result.failure_reason}")
                else:
                    # This is already graphlike - keep it
                    new_dem.append(instruction)
            else:
                # Keep non-error instructions (detectors, observables, etc.)
                new_dem.append(instruction)
        
        # Log summary
        successful = sum(1 for e in hyper_edges 
                        if self.decompose_hyper_edge(e['detectors'], e['probability']).success)
        
        logger.info(f"Successfully decomposed {successful}/{len(hyper_edges)} hyper-edges")
        
        return new_dem
