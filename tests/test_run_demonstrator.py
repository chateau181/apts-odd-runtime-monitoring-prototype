from src.run_demonstrator import main


def test_main_runs_complete_demonstrator(capsys):
    main([])

    captured = capsys.readouterr()

    assert "Scenario Execution: DS-01" in captured.out
    assert "Cycles: 5" in captured.out

    assert "Cycle: 1" in captured.out
    assert "Cycle: 2" in captured.out
    assert "Cycle: 3" in captured.out
    assert "Cycle: 4" in captured.out
    assert "Cycle: 5" in captured.out

    assert "Assessment: Inside ODD" in captured.out
    assert "Assessment: Outside ODD" in captured.out
    assert "Assessment: Unclear" in captured.out

def test_main_runs_unmappable_edge_case(capsys):
    main(["--scenario", "ec-unmappable"])

    captured = capsys.readouterr()

    assert "Scenario Execution: EC-Unmappable" in captured.out
    assert "A-02: Unresolved" in captured.out
    assert "Assessment: Unclear" in captured.out
    assert "Primary Response: Clarification" in captured.out

def test_main_runs_mixed_edge_case(capsys):
    main(["--scenario", "ec-mixed"])

    captured = capsys.readouterr()

    assert "Scenario Execution: EC-Mixed" in captured.out
    assert "A-01: Unresolved" in captured.out
    assert "A-02: Violated" in captured.out
    assert "Assessment: Outside ODD" in captured.out
    assert "Primary Response: Intervention" in captured.out