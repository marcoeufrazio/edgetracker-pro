from analytics.exporters import export_csv, export_markdown


def test_export_csv_writes_rows_to_file(tmp_path) -> None:
    rows = [{"col_a": 1, "col_b": "x"}]
    output_path = tmp_path / "metrics_summary.csv"

    exported_path = export_csv(rows, output_path)

    assert exported_path == output_path
    assert output_path.exists()
    assert "col_a" in output_path.read_text(encoding="utf-8")


def test_export_markdown_writes_text_to_file(tmp_path) -> None:
    output_path = tmp_path / "report_summary.md"
    exported_path = export_markdown("# Title", output_path)

    assert exported_path == output_path
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8") == "# Title"
