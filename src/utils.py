import subprocess
import time
from datetime import date, datetime, timedelta

from colors import Base16ColorScheme


def notify(title: str, msg: str):
    subprocess.Popen(["dunstify", title, msg])


def get_today():
    return datetime.today().date()


def generate_css_vars_from_colorscheme(colorscheme: Base16ColorScheme):
    return ";\n".join(
        [
            f"$base0{hex(i).replace('0x','').upper()}: {c}"
            for i, c in enumerate(colorscheme)
        ]
    )


def get_weekday_names(start_from_sunday: bool = True):
    return (
        (
            date.fromisocalendar(get_today().year, 1, i + 1)
            - timedelta(days=1 if start_from_sunday else 0)
        ).strftime("%A")
        for i in range(7)
    )


def get_last_day_of_month(year: int, month: int):
    if month == 12:
        last_day_of_month = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day_of_month = date(year, month + 1, 1) - timedelta(days=1)
    return last_day_of_month


def get_initial_date_of_monthly_calendar(year: int, month: int):
    first_day_of_month = date(year, month, 1)
    week_of_first_day = first_day_of_month.isocalendar().week
    if first_day_of_month.weekday() != 6:
        week_of_first_day -= 1
        if week_of_first_day == 0:
            week_of_first_day = 52
            year -= 1
    initial_date = date.fromisocalendar(year, week_of_first_day, 7)
    return initial_date


def get_final_date_of_monthly_calendar(year: int, month: int):
    last_day_of_month = get_last_day_of_month(year, month)
    week_of_last_day = last_day_of_month.isocalendar().week
    if last_day_of_month.weekday() == 6:
        week_of_last_day += 1
        if week_of_last_day == 53:
            week_of_last_day = 1
            year += 1
    final_date = date.fromisocalendar(year, week_of_last_day, 6)
    return final_date


def get_ttl_hash(seconds=60):
    """Return the same value withing `seconds` time period"""
    return round(time.time() / seconds)
