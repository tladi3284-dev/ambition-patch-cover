import csv
import json
from pathlib import Path
from typing import List

from .format_classifier import ClassificationResult, classify_file


def scan_directory(source_root: Path) -> List[ClassificationResult]:
    source_root = Path(source_root)
    results = []
    for path in sorted(source_root.rglob("*")):
        if path.is_file():
            results.append(classify_file(path))
    return results


def write_scan_report(results: List[ClassificationResult], output_dir: Path) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "scan_report.json"
    csv_path = output_dir / "scan_report.csv"

    rows = [
        {
            "path": str(r.path),
            "file_format": r.file_format.value,
            "support_status": r.support_status.value,
            "reason": r.reason,
        }
        for r in results
    ]
    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "file_format", "support_status", "reason"])
        writer.writeheader()
        writer.writerows(rows)

    return {"json": json_path, "csv": csv_path, "file_count": len(rows)}
