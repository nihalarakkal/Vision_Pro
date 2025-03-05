
from django.urls import path, include


from core.api.views import (
    hello, HomeView, ProductDetail,
    OrderSummary, UserProfileView,BaseView,
)

app_name = "core_api"


urlpatterns = [

    path('order-summary/', OrderSummary.as_view(), name='order_summary'),
    path('user-profile/', UserProfileView.as_view(), name='user_profile'),
    path('hello/', hello, name='hello'),
    path('home', HomeView.as_view(), name='home'),
    path('<slug>/', ProductDetail.as_view(), name='details'),
    path('',BaseView.as_view(),name="base"),
    




    # path('rest_auth/', include('rest_auth.urls')),
    # path('rest_auth/registration/', include('rest_auth.registration.urls')),
]