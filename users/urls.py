from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('user', UserAPIView, basename='User')
urlpatterns= [
    path('', include(router.urls)),
    path('login/',LoginAPIView.as_view(),name='Login'),
    path('logout/',LogoutAPIView.as_view(),name='Logoutapiview')
    # path('reset_password/', ResetPasswordAPIView.as_view(), name='reset-password'),
]