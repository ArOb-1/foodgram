from django_filters import rest_framework as filters

from recipes.models import Recipe, Ingredient


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(method='filter_tags')
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        if tags:
            return queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return queryset
        if value == 1:
            return queryset.filter(in_favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated:
            return queryset
        if value == 1:
            return queryset.filter(in_shopping_cart__user=user)
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
