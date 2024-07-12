
from django.contrib import admin
from django.urls import path, include,re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib.staticfiles.views import serve as static_serve

schema_view = get_schema_view(
    openapi.Info(
        title="Vision Intelligence",
        default_version='v1',
        description="These are the api's and they are used for building the Vision Intelligence Product.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="saithimma@ekfrazo.in"),
        license=openapi.License(name="Awesome License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    # url=f"https://hul.aivolved.in"
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # to obtain the refresh token and access token 
    # path('api/token_pair/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # to obtain the refersh token 
    path('api/refresh_token/', TokenRefreshView.as_view(), name='token_refresh'),
    # to verify the token 
    # path('api/verify_token/', TokenVerifyView.as_view(), name='token_verify'),

    path('api/', include('dashboard.urls')),
    path('api/', include('users.urls')),


    
    # Swagger UI URLs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Final catch-all pattern to serve index.html for single-page applications
urlpatterns += [re_path(r'^.*$', static_serve, {'path': 'index.html'})]