from django.urls import path, include
from .views import product_list


urlpatterns = [
    path('', product_list, name='product_list'),
    path('api/v1/', include('products.api.v1.urls'))
]
