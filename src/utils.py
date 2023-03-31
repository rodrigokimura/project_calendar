import subprocess
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
