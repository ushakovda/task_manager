from django import template

register = template.Library()

@register.filter
def time_label(total_hours):  # Кастомный фильтр для корректного отображения часов и минут
    hours = int(total_hours)  # Целое число часов
    minutes = int((total_hours - hours) * 60)  # Оставшиеся минуты

    # Определение падежа для часов
    if hours % 10 == 1 and hours % 100 != 11:
        hours_str = f"{hours} час"
    elif 2 <= hours % 10 <= 4 and (hours % 100 < 10 or hours % 100 >= 20):
        hours_str = f"{hours} часа"
    else:
        hours_str = f"{hours} часов"

    # Определение падежа для минут
    if minutes % 10 == 1 and minutes % 100 != 11:
        minutes_str = f"{minutes} минута"
    elif 2 <= minutes % 10 <= 4 and (minutes % 100 < 10 or minutes % 100 >= 20):
        minutes_str = f"{minutes} минуты"
    else:
        minutes_str = f"{minutes} минут"

    # Возвращаем строку с часами и минутами
    if hours > 0 and minutes > 0:
        return f"{hours_str} {minutes_str}"
    elif hours > 0:
        return hours_str
    elif minutes > 0:
        return minutes_str
    else:
        return "0 минут"
