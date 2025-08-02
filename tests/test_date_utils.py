import pytest
from fundman.utils.date_utils import parse_date, days_between, days_remaining_on


class TestParseDate:
    def test_parse_date_iso_dash(self):
        assert parse_date("2025-08-01") == "2025-08-01"

    def test_parse_date_iso_slash(self):
        assert parse_date("2025/08/01") == "2025-08-01"

    def test_parse_date_iso_dot(self):
        assert parse_date("2025.08.01") == "2025-08-01"

    def test_parse_date_chinese(self):
        assert parse_date("2025年08月01日") == "2025-08-01"

    def test_parse_date_mixed_delimiters(self):
        assert parse_date("2025年8月1日") == "2025-08-01"

    def test_parse_date_strip_spaces(self):
        assert parse_date("  2025-08-01  ") == "2025-08-01"

    def test_parse_date_empty_raises(self):
        with pytest.raises(ValueError):
            parse_date("")

    def test_parse_date_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_date("invalid-date")


class TestDaysBetween:
    def test_same_day(self):
        assert days_between("2025-08-01", "2025-08-01") == 0

    def test_cross_month(self):
        assert days_between("2025-07-31", "2025-08-01") == 1

    def test_cross_year(self):
        assert days_between("2024-12-31", "2025-01-01") == 1


class TestDaysRemainingOn:
    def test_remaining_future(self):
        assert days_remaining_on("2025-08-10", "2025-08-01") == 9

    def test_remaining_today_zero(self):
        assert days_remaining_on("2025-08-01", "2025-08-01") == 0

    def test_remaining_past_zero(self):
        assert days_remaining_on("2025-07-01", "2025-08-01") == 0