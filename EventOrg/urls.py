"""
URL configuration for EventOrg project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions, views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import views as auth_views
# from EventOrg.MusicEventOrg.views import UserRegistrationView, initiate_esewa_payment_view, esewa_success, esewa_failure
# from MusicEventOrg.views import  initiate_esewa_payment_view, esewa_success, esewa_failure
# UserRegistrationView,
# from MusicEventOrg import views
# # from MusicEventOrg.views import scan_qr_code
from MusicEventOrg.admin import custom_admin_site
from MusicEventOrg import views as app_views # Correct import


schema_view = get_schema_view(
    openapi.Info(
        title="MusicEvent Handling API",
        default_version='v1',
        description="API for managing music festivals, tickets, payments, and more.",
        terms_of_service="https://www.yubajosh.com/terms/",
        contact=openapi.Contact(email="Music@yubajosh.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticatedOrReadOnly],
)

urlpatterns = [
    # Admin Panel
    # path('admin/', admin.site.urls),

    # Grappelli
    # path('grappelli/', include('grappelli.urls')),
    path('admin/', custom_admin_site.urls),
    # API Endpoints
    path('api/', include('MusicEventOrg.urls')),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    # Login Endpoint
    path('api-auth/', include('rest_framework.urls')),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # ReDoc UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # # UserRegistrationView
    # path('api/register/', UserRegistrationView.as_view(), name='user-registration'),
    # path('api/register/', UserRegistrationView.as_view(), name='user-registration'),

    # CustomTokenObtainPairView
    # path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Admin site
    # path('admin/', admin.site.urls),

    # Registration endpoint
    # path('api/register/', UserRegistrationView.as_view(), name='user-registration'),

    # Login and Logout endpoints
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),


    # Password Reset (Optional)
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    # path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Include other app URLs (if applicable)
    path('', include('MusicEventOrg.urls')),

    # Esewa Payment URLS
    # path('api/initiate-esewa-payment/', initiate_esewa_payment_view, name='initiate-esewa-payment'),
    # path('api/esewa-success/', esewa_success, name='esewa-success'),
    # path('api/esewa-failure/', esewa_failure, name='esewa-failure'),
    # path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    # path('esewa/callback/', views.payment_callback, name='payment_callback'),
    # QR
    # path('api/scan-qr-code/', scan_qr_code, name='scan-qr-code'),
    path('login/', app_views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name= 'logout'),


    path('performers/', app_views.performers, name= 'performers'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Also serve from STATICFILES_DIRS
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()