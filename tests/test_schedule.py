from run_automation import SCHEDULE_CRON, SCHEDULE_DAYS, SCHEDULE_HOURS, SCHEDULE_TIMEZONE, show_schedule

def test_schedule_constants():
    assert SCHEDULE_TIMEZONE == "Europe/London"
    assert SCHEDULE_CRON == "0 8-16 * * 1-5"
    assert len(SCHEDULE_DAYS) == 5
    assert len(SCHEDULE_HOURS) == 9
    assert 17 not in SCHEDULE_HOURS
    assert 8 in SCHEDULE_HOURS
    assert 16 in SCHEDULE_HOURS
    assert len(SCHEDULE_DAYS) * len(SCHEDULE_HOURS) == 45

def test_show_schedule_output(capsys):
    show_schedule()
    captured = capsys.readouterr().out
    assert "Europe/London" in captured
    assert "0 8-16 * * 1-5" in captured
    assert "No run at 17:00" in captured
    assert "Monday 08:00" in captured
    assert "Friday 16:00" in captured
    assert "Total executions per week: 45" in captured
