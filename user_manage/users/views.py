from django.contrib.auth import login, logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccessRoleRule
from .permissions import BusinessElementPermission, IsAdminUser
from .serializers import (
    AccessRoleRuleSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            login(request, user)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        user.first_name = request.data.get("first_name", user.first_name)
        user.last_name = request.data.get("last_name", user.last_name)
        user.username = request.data.get("username", user.username)
        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        return Response(status=status.HTTP_200_OK)


# моки для проверки прав доступа
class MockProductListCreateView(APIView):
    """
    Мок для работы с товарами (business_element = 'products')
    """

    permission_classes = [IsAuthenticated, BusinessElementPermission]
    business_element_name = "products"

    def get(self, request):
        # Мок-список товаров (свои и чужие)
        products = [
            {"id": 1, "name": "Мой товар", "owner_id": request.user.id},
            {"id": 2, "name": "Чужой товар", "owner_id": 999},
        ]
        return Response({"products": products})

    def post(self, request):
        # Создание товара
        return Response(
            {
                "message": "Товар создан",
                "product": {
                    "id": 3,
                    "name": request.data.get("name", "Новый товар"),
                    "owner_id": request.user.id,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class MockProductDetailView(APIView):
    """
    Детальная работа с товаром
    """

    permission_classes = [IsAuthenticated, BusinessElementPermission]
    business_element_name = "products"

    def get(self, request, pk):
        # Создаём мок-объект с owner_id (предполагаем, что товар наш)
        mock_product = type(
            "Product",
            (),
            {"id": pk, "name": f"Товар {pk}", "owner_id": request.user.id},
        )
        self.check_object_permissions(request, mock_product)
        return Response({"id": pk, "name": f"Товар {pk}", "owner_id": request.user.id})

    def delete(self, request, pk):
        mock_product = type("Product", (), {"id": pk, "owner_id": request.user.id})
        self.check_object_permissions(request, mock_product)
        return Response({"message": f"Товар {pk} удалён"})


class AccessRuleListCreateView(APIView):
    """
    Мок для управления правилами доступа.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        rules = AccessRoleRule.objects.all()
        serializer = AccessRoleRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AccessRoleRuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccessRuleDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get_object(self, pk):
        try:
            return AccessRoleRule.objects.get(pk=pk)
        except AccessRoleRule.DoesNotExist:
            return None

    def put(self, request, pk):
        rule = self.get_object(pk)
        if not rule:
            return Response(
                {"error": "Правило не найдено"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = AccessRoleRuleSerializer(rule, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        rule = self.get_object(pk)
        if not rule:
            return Response(
                {"error": "Правило не найдено"}, status=status.HTTP_404_NOT_FOUND
            )
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
