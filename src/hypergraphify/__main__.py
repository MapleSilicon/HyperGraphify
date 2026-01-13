import argparse
import stim
from hypergraphify import HyperGraphTransformer

def main():
    p = argparse.ArgumentParser(prog="hypergraphify", description="Transform Stim DEM hyper-edges into graphlike chains.")
    p.add_argument("input", help="Input .dem file")
    p.add_argument("-o", "--output", required=True, help="Output .dem file")
    args = p.parse_args()

    dem = stim.DetectorErrorModel.from_file(args.input)
    out = HyperGraphTransformer().transform(dem)
    out.to_file(args.output)

    print(f"Wrote: {args.output}")

if __name__ == "__main__":
    main()
