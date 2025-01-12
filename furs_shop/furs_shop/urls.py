from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('', include('products.urls')),
    path('', include('orders.urls')),
    path('users/', include('users.urls')),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/docs', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('api/redoc', SpectacularRedocView.as_view(), name='redoc'),
    path('api/schema', SpectacularAPIView.as_view(), name='schema'),
]
