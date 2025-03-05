from django.urls import path
from Staff import views

urlpatterns= [
                path('staff_home',views.staff_home,name="staff_home"),
]
