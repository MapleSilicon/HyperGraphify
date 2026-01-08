# HyperGraphify

Transform quantum LDPC codes for MWPM decoding by decomposing hyper-edges into graphlike chains.

## What It Does

HyperGraphify converts non-graphlike detector error models (with hyper-edges involving 3+ detectors) into graphlike forms compatible with Minimum-Weight Perfect Matching (MWPM) decoders like PyMatching.

## Installation

```bash
git clone https://github.com/yourusername/HyperGraphify.git
cd HyperGraphify
pip install -e .
import stim
from hypergraphify import HyperGraphTransformer

# Create DEM with hyper-edges
dem = stim.DetectorErrorModel("""
    error(0.1) D0 D1 D2
    detector D0
    detector D1
    detector D2
    logical_observable L0
""")

# Transform to graphlike form
transformer = HyperGraphTransformer()
transformed = transformer.transform(dem)

print("Transformed DEM:")
print(transformed)
