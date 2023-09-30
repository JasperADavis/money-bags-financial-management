import calendar
from datetime import datetime, timedelta
from flask import redirect, session, render_template
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(text=None):
    if text == None:
        return render_template("apology.html", text="Sorry, you've encountered a problem!)")
    else:
        return render_template("apology.html", text=text)


def get_last_day_of_month():
    today = datetime.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return today.replace(day=last_day).strftime('%Y-%m-%d')


def get_next_due_date(day):
    today = datetime.today()
    if day.upper() == "EOM":
        return get_last_day_of_month()
    else:
        day = int(day)
        if today.day <= day:
            target_date = today.replace(day=day)
        else:
            next_month = today.replace(day=28) + timedelta(days=4)  # Handle end of month edge case
            target_date = next_month.replace(day=day)

        return target_date.strftime('%Y-%m-%d')


def none_look(value):
    if value:
        return value
    else:
        return "-"


def time(input_time):
    if not input_time:
        return none_look(None)
    else:
        # Parse the input time string
        time_obj = datetime.strptime(input_time, "%H:%M")

        # Format the time as "HH:MM AM/PM"
        formatted_time = time_obj.strftime("%I:%M %p")

        return formatted_time


def usd(value):
    """Format value as USD."""
    if value == 0 or value == "0":
        return f"${value:,.2f}"
    elif not value:
        return none_look(None)
    elif value < 0:
        return f"-${(-1 * value):,.2f}"
    else:
        return f"${value:,.2f}"


def pct(value):
    """Format value as percent."""
    if value == "-":
        return none_look(value)
    else:
        return f"{(float(value) * 100):.2f}%"