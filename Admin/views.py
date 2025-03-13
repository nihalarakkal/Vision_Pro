from django.shortcuts import render,redirect
from django.views.generic import TemplateView
from core.models import Item

# Create your views here.

class homeTemplateView(TemplateView):
    template_name="admin_home.html"
