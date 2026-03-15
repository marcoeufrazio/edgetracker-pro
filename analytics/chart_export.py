from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure


def export_chart(figure: Figure, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, format="png", dpi=150)
    return path
