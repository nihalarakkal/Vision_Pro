from django.urls import path
from Admin.views import homeTemplateView
from Admin import views
from .views import order_list,user_list


app_name = "Admin"

urlpatterns= [
             path('', homeTemplateView.as_view(), name="admin"),
             path('login_page/',views.login_page,name="login_pages"),
             path('admin_login/',views.admin_login,name="Admin_login"),
             path('admin_logout/',views.admin_logout,name="Admin_logout"),
             path('product_page/',views.product_page,name="admin_products"),
             path('save_products/',views.admin_save_products,name="admin_save_products"),
             path('edit_products/<int:prd_id>/',views.admin_edit_products,name="admin_edit_products"),
             path('update_products/<int:prd_id>/',views.admin_update_products,name="admin_update_products"),
             path('delete_products/<int:prd_id>/',views.admin_delete_products,name="admin_delete_products"),
             path('display_products/',views.display_products,name='admin_display_products'),
             path("users/", user_list, name="user_list"),
             path('orderd/',order_list,name="order_list")

]
