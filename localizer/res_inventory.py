import json
from pathlib import Path
from typing import List

from .format_classifier import ClassificationResult, classify_file


def inventory_res_folder(res_path: Path) -> List[ClassificationResult]:
    """
    Read-only listing only (principle 1 + spec 4.3): never assumes SUPPORTED
    for res/*.N11 image containers, since no sample has been structurally
    analyzed yet. Reuses format_classifier's honest CONDITIONAL/UNKNOWN gate.
    """
    res_path = Path(res_path)
    results = []
    for path in sorted(res_path.rglob("*")):
        if path.is_file():
            results.append(classify_file(path))
    return results


def write_res_inventory(results: List[ClassificationResult], output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "path": str(r.path),
            "file_format": r.file_format.value,
            "support_status": r.support_status.value,
            "reason": r.reason,
        }
        for r in results
    ]
    output_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
