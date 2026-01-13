import subprocess
import sys
from pathlib import Path
import stim

def test_cli_roundtrip(tmp_path: Path):
    inp = tmp_path / "in.dem"
    out = tmp_path / "out.dem"

    stim.DetectorErrorModel("error(0.1) D0 D1 D2").to_file(str(inp))

    r = subprocess.run([sys.executable, "-m", "hypergraphify", str(inp), "-o", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert out.exists()
