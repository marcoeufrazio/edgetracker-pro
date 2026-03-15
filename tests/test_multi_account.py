from pathlib import Path

from analytics.multi_account import analyze_multiple_accounts


SAMPLE_STATEMENT_PATH = Path("data/imports/mt4_statement.html")


def test_analyze_multiple_accounts_returns_account_level_results() -> None:
    analyses = analyze_multiple_accounts([SAMPLE_STATEMENT_PATH])

    assert len(analyses) == 1
    assert analyses[0].account_id == "24601985"
    assert analyses[0].dashboard_data.performance.total_trades == 247
    assert analyses[0].health_classification
