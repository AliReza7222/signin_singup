from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class Home(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'pages/home.html'
