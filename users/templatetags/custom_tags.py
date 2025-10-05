from django import template
from django.contrib.auth.models import Group
from users.models import CustomUser
from appmodels.models import Subscription
from django.utils import timezone

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False


@register.filter(name='is_premium')
def is_premium(user):
    """
    Tag to ask if some user has an active subscription
    """
    today = timezone.now().date()
    has_active_subscription = Subscription.objects.filter(
        user=user,
        due_date__gte=today,
        status='ACTIVE'
    ).exists()
    return has_active_subscription


@register.filter(name='split')
def split(value, delimiter=','):
    """
    Returns a list of strings by splitting the input on the delimiter
    """
    if value:
        return value.split(delimiter)
    return []


@register.filter(name='trim')
def trim(value):
    """
    Removes leading and trailing whitespace
    """
    if value:
        return value.strip()
    return value


@register.filter(name='days_until')
def days_until(date):
    """
    Returns the number of days until the given date
    """
    if date:
        today = timezone.now().date()
        delta = date - today
        return delta.days
    return 0