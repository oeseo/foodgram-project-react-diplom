from rest_framework.validators import ValidationError

from users.models import Follow


def validate_following(data, user):
    author = data.get('author')
    if Follow.objects.filter(user=user,
                             author=author).exists():
        raise ValidationError('Вы уже подписаны!')

    if user == author:
        raise ValidationError('Нельзя подписаться на самого себя!')

    return data
