from analytics.targets import calculate_green_target, calculate_traffic_light


def test_calculate_green_target_multiplies_cycle_target_by_one_point_five() -> None:
    assert calculate_green_target(200.0) == 300.0


def test_calculate_traffic_light_returns_red_below_sixty_percent() -> None:
    assert calculate_traffic_light(current_profit=100.0, green_target=300.0) == "red"


def test_calculate_traffic_light_returns_yellow_below_green_target() -> None:
    assert calculate_traffic_light(current_profit=250.0, green_target=300.0) == "yellow"


def test_calculate_traffic_light_returns_green_at_or_above_target() -> None:
    assert calculate_traffic_light(current_profit=300.0, green_target=300.0) == "green"
