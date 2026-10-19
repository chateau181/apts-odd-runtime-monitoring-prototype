from pathlib import Path

from src.scenario_loader import load_runtime_scenario


def test_load_runtime_scenario():
    scenario = load_runtime_scenario()

    assert scenario.scenario_id == "DS-01"
    assert (
        scenario.description
        == "Predefined dynamic patient transport scenario for the minimal prototype."
    )

    assert len(scenario.cycles) == 5
    assert [cycle.cycle for cycle in scenario.cycles] == [
        1,
        2,
        3,
        4,
        5,
    ]

def test_cycle_three_preserves_missing_heart_rate():
    scenario = load_runtime_scenario()

    cycle_three = scenario.cycles[2]

    assert cycle_three.cycle == 3
    assert cycle_three.snapshot["heart_rate"] is None
    assert "surface_condition" not in cycle_three.snapshot

def test_cycle_four_contains_wet_surface():
    scenario = load_runtime_scenario()

    cycle_four = scenario.cycles[3]

    assert cycle_four.cycle == 4
    assert cycle_four.snapshot["surface_condition"] == "Wet"
    assert cycle_four.snapshot["vehicle_speed"] == 1.2
    assert cycle_four.snapshot["heart_rate"] == 85

def test_load_unmappable_edge_case():
    scenario = load_runtime_scenario(
        Path("data/scenarios/ec_unmappable.json")
    )

    assert scenario.scenario_id == "EC-Unmappable"
    assert len(scenario.cycles) == 1

    snapshot = scenario.cycles[0].snapshot

    assert (
        snapshot["surface_condition"]
        == "Unsupported_surface_state"
    )
    assert snapshot["heart_rate"] == 85

def test_load_mixed_edge_case():
    scenario = load_runtime_scenario(
        Path("data/scenarios/ec_mixed.json")
    )

    assert scenario.scenario_id == "EC-Mixed"
    assert len(scenario.cycles) == 1

    snapshot = scenario.cycles[0].snapshot

    assert snapshot["surface_condition"] == "Wet"
    assert snapshot["heart_rate"] is None
    assert snapshot["vehicle_speed"] == 1.2