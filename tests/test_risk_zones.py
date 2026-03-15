from analytics.risk_zones import classify_risk_zone


def test_classify_risk_zone_returns_green_below_five_percent() -> None:
    assert classify_risk_zone(4.99) == "green"


def test_classify_risk_zone_returns_yellow_between_five_and_ten_percent() -> None:
    assert classify_risk_zone(5.0) == "yellow"
    assert classify_risk_zone(9.99) == "yellow"


def test_classify_risk_zone_returns_red_at_or_above_ten_percent() -> None:
    assert classify_risk_zone(10.0) == "red"
