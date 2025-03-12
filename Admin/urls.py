from django.urls import path
from Admin.views import homeTemplateView
from Admin import views


app_name = "Admin"

urlpatterns= [
             path('', homeTemplateView.as_view(), name="admin"),
]
