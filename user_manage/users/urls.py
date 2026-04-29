from django.urls import path
from .views import (RegisterView, LoginView, LogoutView,
                    UserProfileView, DeleteAccountView,
                    MockProductListCreateView, AccessRuleListCreateView,
                    AccessRuleDetailView, MockProductDetailView)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('delete/', DeleteAccountView.as_view(), name='delete'),

    path('mock/products/', MockProductListCreateView.as_view(), name='mock-products'),
    path('mock/products/<int:pk>/', MockProductDetailView.as_view(), name='mock-product-detail'),

    path('admin/rules/', AccessRuleListCreateView.as_view(), name='admin-rules'),
    path('admin/rules/<int:pk>/', AccessRuleDetailView.as_view(), name='admin-rule-detail'),
]
