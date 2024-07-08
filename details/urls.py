from django.urls import path
from . import views


urlpatterns = [
    path('auth/register', views.user_register, name="register"),
    path('auth/login', views.login , name="login"),
    path('api/users/<int:id>', views.users_record , name="record"),
    path('api/organisations', views.current_user_membership.as_view() , name="membership"),
    path("api/organisations/<int:orgId>/users", views.user_orgg, name="user_orgg"),
    path('api/organisations/<int:orgId>', views.organization_details , name="org_details")
]
