from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = [
    ROOT / "examples" / "save_and_load_json_demo.py",
    ROOT / "examples" / "patent_valuation_style_report.py",
    ROOT / "examples" / "full_report_workflow_demo.py",
]


def test_selected_examples_run_successfully() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")

    for example in EXAMPLES:
        result = subprocess.run(
            [sys.executable, str(example)],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr or result.stdout
