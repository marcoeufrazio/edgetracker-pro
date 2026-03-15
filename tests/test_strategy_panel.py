from dashboard.strategy_panel import render_strategy_analyzer_panel, render_trade_intelligence_panel


def test_strategy_panel_exports_render_functions() -> None:
    assert callable(render_trade_intelligence_panel)
    assert callable(render_strategy_analyzer_panel)
