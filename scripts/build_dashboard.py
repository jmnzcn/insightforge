"""Validate dashboard-as-code configuration and compile a static JSON data bundle."""
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def compile_dashboard(config_path: Path, data_path: Path) -> dict:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not config.get("title"):
        raise ValueError("Dashboard must have a title")
    metrics = config.get("metrics", [])
    charts = config.get("charts", [])
    dimensions = config.get("dimensions", [])
    if not metrics or not charts:
        raise ValueError("Dashboard requires metrics and charts")
    ids = [m["id"] for m in metrics]
    if len(ids) != len(set(ids)):
        raise ValueError("Metric IDs must be unique")
    with data_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        required = {config["date_column"], *dimensions, *(m["column"] for m in metrics)}
        missing = required - fields
        if missing:
            raise ValueError(f"Missing CSV columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError("Dataset must not be empty")
    for chart in charts:
        if chart["metric"] not in ids:
            raise ValueError(f"Unknown chart metric: {chart['metric']}")
        if chart["x"] not in fields:
            raise ValueError(f"Unknown chart dimension: {chart['x']}")
        if chart["type"] not in {"line", "bar", "donut"}:
            raise ValueError(f"Unsupported chart type: {chart['type']}")
    for index, row in enumerate(rows, start=2):
        try:
            date.fromisoformat(row[config["date_column"]])
            for metric in metrics:
                raw = row[metric["column"]]
                value = float(raw)
                if not __import__("math").isfinite(value) or value < 0:
                    raise ValueError("Values must be finite and non-negative")
                row[metric["column"]] = value
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid data at CSV line {index}: {exc}") from exc
    return {"config": config, "rows": rows, "row_count": len(rows)}


def main() -> None:
    bundle = compile_dashboard(ROOT / "dashboard.yaml", ROOT / "data/sales.csv")
    target = ROOT / "site/dashboard.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Validated {bundle['row_count']} rows; wrote {target}")


if __name__ == "__main__":
    main()
