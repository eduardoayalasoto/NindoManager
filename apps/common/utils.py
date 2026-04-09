from django.utils import timezone


def get_today():
    return timezone.now().date()


def get_day_of_week_spanish(date=None):
    """Returns Spanish name for day of week."""
    if date is None:
        date = get_today()
    days = {
        0: "Lunes", 1: "Martes", 2: "Miércoles",
        3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo"
    }
    return days[date.weekday()]


def get_day_of_week_english(date=None):
    """Returns English name for day of week (for recurring_pattern matching)."""
    if date is None:
        date = get_today()
    days = {
        0: "Monday", 1: "Tuesday", 2: "Wednesday",
        3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
    }
    return days[date.weekday()]
