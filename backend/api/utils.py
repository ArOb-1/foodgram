from django.http import HttpResponse


def generate_shopping_list_text(ingredients):
    """Генерирует текст списка покупок."""
    lines = []
    for item in ingredients:
        lines.append(
            f"{item['ingredient__name']} "
            f"({item['ingredient__measurement_unit']}) - "
            f"{item['total']}"
        )
    return '\n'.join(lines)


def create_shopping_list_response(ingredients):
    """Создает HttpResponse со списком покупок."""
    content = generate_shopping_list_text(ingredients)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.txt"'
    )
    return response


def to_base36(self, num):
    chars = '0123456789abcdefghijklmnopqrstuvwxyz'
    if num == 0:
        return '0'
    result = ''
    while num:
        num, i = divmod(num, 36)
        result = chars[i] + result
    return result
