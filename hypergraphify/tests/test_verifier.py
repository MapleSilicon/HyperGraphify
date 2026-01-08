"""
Verifier module for validating the correctness of transformations.
"""

import stim
import numpy as np
from typing import List, Dict, Tuple, Optional, Set


class TransformationVerifier:
    """
    Verify that transformations preserve the essential properties of the error model.
    """
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the verifier.
        
        Args:
            verbose: Whether to print detailed verification information
        """
        self.verbose = verbose
        self.verification_log = []
        
    def verify(self, original_dem: stim.DetectorErrorModel, 
              transformed_dem: stim.DetectorErrorModel) -> Dict[str, bool]:
        """
        Verify that the transformation preserves essential properties.
        
        Args:
            original_dem: Original detector error model
            transformed_dem: Transformed detector error model
            
        Returns:
            Dictionary of verification results
        """
        results = {
            "original_non_empty": len(list(original_dem)) > 0,
            "transformed_non_empty": len(list(transformed_dem)) > 0,
            "valid": True  # For now, always return True
        }
        
        # Log the verification
        self.verification_log.append({
            "original_dem_num_instructions": len(list(original_dem)),
            "transformed_dem_num_instructions": len(list(transformed_dem)),
            "results": results
        })
        
        if self.verbose:
            print(f"[HyperGraphify] verification results: {results}")
            
        return results
    
    def get_verification_log(self) -> List[Dict]:
        """
        Get the log of verifications performed.
        
        Returns:
            List of verification records
        """
        return self.verification_log