from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from recipes.models import (
    Recipe, Ingredient, Tag,
    Favourite, ShoppingCart, Subscription, RecipeIngredient
)
from .serializers import (
    RecipeReadSerializer, RecipeWriteSerializer, RecipeShortSerializer,
    IngredientSerializer, TagSerializer,
    UserSerializer, UserCreateSerializer, UserWithRecipesSerializer, AvatarSerializer
)
from .filters import RecipeFilter, IngredientFilter
from .permissions import IsAuthorOrReadOnly


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            if Favourite.objects.filter(user=user, recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном.'}, status=status.HTTP_400_BAD_REQUEST)
            Favourite.objects.create(user=user, recipe=recipe)
            return Response(RecipeShortSerializer(recipe, context={'request': request}).data, status=status.HTTP_201_CREATED)
        favorite = Favourite.objects.filter(user=user, recipe=recipe).first()
        if not favorite:
            return Response({'errors': 'Рецепт не в избранном.'}, status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(RecipeShortSerializer(recipe, context={'request': request}).data, status=status.HTTP_201_CREATED)
        cart_item = ShoppingCart.objects.filter(user=user, recipe=recipe).first()
        if not cart_item:
            return Response({'errors': 'Рецепта нет в списке покупок.'}, status=status.HTTP_400_BAD_REQUEST)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total=Sum('amount')).order_by('ingredient__name')
        lines = [
            f"{item['ingredient__name']} ({item['ingredient__measurement_unit']}) — {item['total']}"
            for item in ingredients
        ]
        content = '\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        code = self._to_base36(recipe.id)
        short_url = request.build_absolute_uri(f'/s/{code}')
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)

    def _to_base36(self, num):
        chars = '0123456789abcdefghijklmnopqrstuvwxyz'
        if num == 0:
            return '0'
        result = ''
        while num:
            num, i = divmod(num, 36)
            result = chars[i] + result
        return result


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_value_regex = r'\d+'

    def get_permissions(self):
        if self.action in ('me', 'avatar', 'subscribe', 'subscriptions'):
            return (IsAuthenticated(),)
        return (AllowAny(),)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('subscriptions', 'subscribe'):
            return UserWithRecipesSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        output = UserSerializer(user, context={'request': request}).data
        return Response(output, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='set_password')
    def set_password(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not current_password or not new_password:
            return Response(
                {'current_password': ['Обязательное поле.'], 'new_password': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not request.user.check_password(current_password):
            return Response(
                {'current_password': ['Неверный пароль.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        request.user.set_password(new_password)
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        if user.avatar:
            user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request):
        authors = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(authors)
        serializer = UserWithRecipesSerializer(page or authors, many=True, context={'request': request})
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, id=pk)
        user = request.user
        if request.method == 'POST':
            if author == user:
                return Response({'errors': 'Нельзя подписаться на самого себя.'}, status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Вы уже подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=user, author=author)
            serializer = UserWithRecipesSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(user=user, author=author).first()
        if not subscription:
            return Response({'errors': 'Вы не подписаны на этого пользователя.'}, status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def short_link_redirect(request, code):
    recipe_id = _from_base36(code)
    if recipe_id is None:
        return HttpResponse(status=404)
    recipe = Recipe.objects.filter(id=recipe_id).first()
    if not recipe:
        return HttpResponse(status=404)
    return HttpResponseRedirect(f'/recipes/{recipe.id}')


def _from_base36(value):
    try:
        return int(value, 36)
    except ValueError:
        return None
