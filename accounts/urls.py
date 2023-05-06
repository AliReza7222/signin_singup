from django.urls import path

from .views import LoginRegister, Login, Logout


urlpatterns = [
    path('', LoginRegister.as_view(), name='login_register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
]
