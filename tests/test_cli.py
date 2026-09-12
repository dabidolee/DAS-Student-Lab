from das_student_lab.cli import main


def test_info_command_reports_pre_alpha_and_citation(capsys) -> None:
    result = main(["info"])
    output = capsys.readouterr().out

    assert result == 0
    assert "pre-alpha" in output
    assert "10.58046/5J60-FJ89" in output

