from datetime import date

from utils import (
    get_final_date_of_monthly_calendar,
    get_initial_date_of_monthly_calendar,
    get_last_day_of_month,
)


def test_get_last_day_of_month():
    params_to_date = {
        (2023, 2): date(2023, 2, 28),
        (2023, 4): date(2023, 4, 30),
        (2015, 2): date(2015, 2, 28),
        (2023, 12): date(2023, 12, 31),
    }
    for params, expected_date in params_to_date.items():
        assert get_last_day_of_month(*params) == expected_date


def test_get_initial_date_of_monthly_calendar():
    params_to_date = {
        (2023, 2): date(2023, 1, 29),
        (2023, 4): date(2023, 3, 26),
        (2015, 2): date(2015, 2, 1),
        (2024, 1): date(2023, 12, 31),
    }
    for params, expected_date in params_to_date.items():
        assert get_initial_date_of_monthly_calendar(*params) == expected_date


def test_get_final_date_of_monthly_calendar():
    params_to_date = {
        (2023, 2): date(2023, 3, 4),
        (2023, 4): date(2023, 5, 6),
        (2015, 2): date(2015, 2, 28),
        (2023, 12): date(2024, 1, 6),
    }
    for params, expected_date in params_to_date.items():
        assert get_final_date_of_monthly_calendar(*params) == expected_date
