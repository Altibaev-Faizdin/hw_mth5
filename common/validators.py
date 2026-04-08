from datetime import date
from rest_framework import serializers


def validate_price(value):
    if value < 0:
        raise serializers.ValidationError("Цена не может быть отрицательной.")
    return value


def validate_email(value):
    if '@' not in value:
        raise serializers.ValidationError("Введите корректный email-адрес.")
    return value


def validate_text_length(value, min_length=1, max_length=1000):
    if len(value) < min_length:
        raise serializers.ValidationError(
            f"Текст должен быть не менее {min_length} символов."
        )
    if len(value) > max_length:
        raise serializers.ValidationError(
            f"Текст не должен превышать {max_length} символов."
        )
    return value


def validate_age_for_product_creation(request):
    token = getattr(request, 'auth', None)

    if token is None:
        raise serializers.ValidationError("Укажите дату рождения, чтобы создать продукт.")

    birthdate_raw = token.get('birthdate') if hasattr(token, 'get') else None
    if not birthdate_raw:
        raise serializers.ValidationError("Укажите дату рождения, чтобы создать продукт.")

    try:
        birthdate = date.fromisoformat(birthdate_raw)
    except (TypeError, ValueError):
        raise serializers.ValidationError("Укажите дату рождения, чтобы создать продукт.")

    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    if age < 18:
        raise serializers.ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")

    return birthdate
