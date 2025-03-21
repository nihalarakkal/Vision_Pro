from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import View,TemplateView,DetailView
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from core.models import Item,LABEL_CHOICES
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


# Create your views here.

class homeTemplateView(TemplateView):
    template_name="staff_home.html"

def add_products(request):
    cat=Item.objects.values_list('category', flat=True).distinct()
    lab=Item.objects.values_list('label',flat=True).distinct()
    return render(request,"add_products.html",{'lab':lab,'cat':cat})
def display_products(request):
    Products=Item.objects.all()
    return render(request,"display_products.html",{'Products':Products})
def save_products(request):
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
    return redirect("Staff:display_products")
def edit_products(request,prd_id):
    data=Item.objects.get(id=prd_id)
    cat =Item.objects.all()
    return render(request,"edit_products.html",{'data':data,'cat':cat})
# def update_products(request,prd_id):
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
#         img1=request.FILES['img1']
#         img2=request.FILES['img2']
#         fs=FileSystemStorage()
#         file1=fs.save(img1.name, img1)
#         file2=fs.save(img2.name, img2)
#     except MultiValueDictKeyError:
#         file=Item.objects.get(id=prd_id).fview
#         file=Item.objects.get(id=prd_id).sview
#         Item.objects.filter(id=prd_id).update(title=ti,price=pr,discount_price=dp,category=cat,label=lab,slug=slg,description=des, features=fea,fview=file1,sview=file2)
#     return redirect("Staff:display_products")


def update_products(request, prd_id):
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

        return redirect("Staff:display_products")

    return redirect("Staff:display_products")


def delete_products(request,prd_id):
  x=Item.objects.filter(id=prd_id)
  x.delete()
  return redirect("Staff:display_products")

def login_page(request):
    return render(request,"admin_login.html")
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
              return redirect("Staff:staff")
        else:
            messages.error(request,"Invalid Password")
            return redirect("Staff:login_page")
    else:
        messages.warning(request,"user not found")
        return redirect("Staff:login_page")
def admin_logout(request):
    del request.session['username']
    del request.session['password']
    messages.success(request,"Logout Successfully")
    return redirect("Staff:login_page")