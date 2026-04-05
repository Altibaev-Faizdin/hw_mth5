from rest_framework import serializers


def validate_price(value):
    if value < 0:
        raise serializers.ValidationError("Цена не может быть отрицательной.")
    return value


def validate_email(value):
    if '@' not in value:
        raise serializers.ValidationError("Введите корректный email адрес.")
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
