from django.urls import path
from Staff.views import homeTemplateView
from Staff import views


app_name = "Staff"

urlpatterns= [
                path('', homeTemplateView.as_view(), name="staff"),
                path('add_product/',views.add_products,name="add_product"),
                path('display_products/',views.display_products,name='display_products'),
                path('save_products/',views.save_products,name="save_products"),
                path('edit_products/<int:prd_id>/',views.edit_products,name="edit_products"),
                path('update_products/<int:prd_id>/',views.update_products,name="update_products"),
                path('delete_products/<int:prd_id>/',views.delete_products,name="delete_products"),
                path('login_page/',views.login_page,name="login_page"),
                path('admin_login/',views.admin_login,name="admin_login"),
                path('admin_logout/',views.admin_logout,name="admin_logout"),
]
