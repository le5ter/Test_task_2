from django.urls import path, include
from .views import add_to_cart, view_cart, checkout

urlpatterns = [
    path('add_to_cart/<int:product_id>', add_to_cart, name='add_to_cart'),
    path('cart', view_cart, name='view_cart'),
    path('checkout', checkout, name='checkout'),
    path('api/v1/', include('orders.api.v1.urls'))
]
