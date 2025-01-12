from django.urls import path
from .views import CartView, OrderCreateView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('order/', OrderCreateView.as_view(), name='order-create'),
]
