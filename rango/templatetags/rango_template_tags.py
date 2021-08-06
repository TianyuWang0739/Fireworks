from django import template
from rango.models import Category

register = template.Library()


@register.inclusion_tag('rango/categories.html')
def get_category_list(current_category=None):
    return {'categories': Category.objects.all(),
            'current_category': current_category}


@register.filter()
def is_like_product(value, user):
    for i in user.favoriteproduct_set.all():
        if i.product == value:
            return True


@register.filter()
def is_like_page(value, user):
    for i in user.favoritepage_set.all():
        if i.page == value:
            return True
