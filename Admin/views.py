from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import TemplateView
from core.models import Item,UserProfile,OrderItem,Order
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
# Create your views here.

class homeTemplateView(TemplateView):
    template_name="admin_home.html"
def login_page(request):
    return render(request,"login.html")
def admin_login(request):
    if request.method=="POST":
        un = request.POST.get('username')
        pwd = request.POST.get('pass')
        if User.objects.filter(username__contains=un).exists():
            x = authenticate(username=un, password=pwd)
            if x is not None:
              login(request, x)
              request.session['username']=un
              request.session['password']=pwd
              messages.success(request,"Welcome")
              return redirect("Admin:admin")
        else:
            messages.error(request,"Invalid Password")
            return redirect("Admin:login_page")
    else:
        messages.warning(request,"user not found")
        return redirect("Admin:login_page")
def admin_logout(request):
    del request.session['username']
    del request.session['password']
    messages.success(request,"Logout Successfully")
    return redirect("Admin:login_page")
def product_page(request):
    catg=Item.objects.values_list('category', flat=True).distinct()
    labe=Item.objects.values_list('label',flat=True).distinct()
    return render(request,"product.html",{'catg':catg,'labe':labe})
def admin_save_products(request):
    if request.method=="POST":
        ti=request.POST.get('title')
        pr=request.POST.get('price')
        dp=request.POST.get('d_price')
        cat=request.POST.get('category')
        lab=request.POST.get('label')
        slg=request.POST.get('slug')
        des=request.POST.get('description')
        fea=request.POST.get('Features')
        fv=request.FILES['img1']
        sv=request.FILES['img2']
    obj=Item(title=ti,price=pr,discount_price=dp,category=cat,label=lab,slug=slg,description=des, features=fea,fview=fv,sview=sv)
    obj.save()
    return redirect("Admin:display_products")
def admin_edit_products(request,prd_id):
    data=Item.objects.get(id=prd_id)
    cat =Item.objects.all()
    return render(request,"edit_products.html",{'data':data,'cat':cat})
# def admin_update_products(request,prd_id):
#     if request.method=="POST":
#         ti=request.POST.get('title')
#         pr=request.POST.get('price')
#         dp=request.POST.get('d_price')
#         cat=request.POST.get('category')
#         lab=request.POST.get('label')
#         slg=request.POST.get('slug')
#         des=request.POST.get('description')
#         fea=request.POST.get('Features')
#     try:
#         img=request.FILES['image']
#         fs=FileSystemStorage()
#         file=fs.save(img.name, img)
#     except MultiValueDictKeyError:
#         file=Item.objects.get(id=prd_id).fview
#         file=Item.objects.get(id=prd_id).sview
#         Item.objects.filter(id=prd_id).update(title=ti,price=pr,discount_price=dp,category=cat,label=lab,slug=slg,description=des, features=fea,fview=file,sview=file)
#     return redirect("Admin:display_products")


def admin_update_products(request, prd_id):
    product = get_object_or_404(Item, id=prd_id)

    if request.method == "POST":
        # Fetch form data
        ti = request.POST.get('title')
        pr = request.POST.get('price')
        dp = request.POST.get('d_price')
        cat = request.POST.get('category')
        lab = request.POST.get('label')
        slg = request.POST.get('slug')
        des = request.POST.get('description')
        fea = request.POST.get('Features')

        # Handle images
        img1 = request.FILES.get('img1', product.fview)  # Use existing if not uploaded
        img2 = request.FILES.get('img2', product.sview)  # Use existing if not uploaded

        # Update product details
        product.title = ti
        product.price = pr
        product.discount_price = dp
        product.category = cat
        product.label = lab
        product.slug = slg
        product.description = des
        product.features = fea
        product.fview = img1
        product.sview = img2
        product.save()  # Calls model's save method properly

        return redirect("Admin:display_products")

    return redirect("Admin:display_products")
def admin_delete_products(request,prd_id):
  x=Item.objects.filter(id=prd_id)
  x.delete()
  return redirect("Admin:display_products")
def display_products(request):
    Products=Item.objects.all()
    return render(request,"display_products.html",{'Products':Products})
def user_list(request):
    users = User.objects.all()  # Fetch all users
    # Optimized query

    context = {
        "users": users,
      
    }
    return render(request, "user.html", context)
def order_list(request):
    orders = Order.objects.select_related("user").prefetch_related("items") 
    context = {
        
        "orders": orders,
    }
    return render(request,"orders.html",context)