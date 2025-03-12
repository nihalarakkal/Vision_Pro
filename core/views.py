from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import TemplateView, DetailView, ListView, View
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.db.models import Q
from django.views import View
from django.http import HttpResponse

from .forms import CheckoutForm, CouponForm, RefundForm, LensesForm
from .models import Item, Order, OrderItem, Address, Payment, Coupon, Refund, UserProfile, EyeLenses

import stripe
import random, string



stripe.api_key = settings.STRIPE_SECRET_KEY







def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def page_not_found_view(request, exception):
    return render(request, '404.html')
from django.shortcuts import render, redirect





class Home(ListView):
    models = Item
    context_object_name = 'items'
    queryset = Item.objects.all()
    template_name = "home_page.html"
    paginate_by = 10

class Base(ListView):
    models = Item
    context_object_name = 'items'
    queryset = Item.objects.all()
    template_name = "index.html"
    paginate_by = 10
class appointment(ListView):
    models = Item
    context_object_name = 'items'
    queryset = Item.objects.all()
    template_name ="book_appointment.html"
    paginate_by = 10


class OrderSummary(LoginRequiredMixin, View):
    context_object_name = 'cart'
    def get(self, request, *args, **kwargs):
        try:
            order_item = Order.objects.get(user=self.request.user, ordered=False)
            return render(request, 'order_summary.html', {'cart': order_item,})
        except ObjectDoesNotExist:
            messages.warning(request,"You don't have any items in your cart!")
            return redirect('core:home')


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
        return valid


class Checkout(View):
    def get(self, request, *args, **kwargs):
        qs = Order.objects.filter(user=self.request.user, ordered=False)
        if qs.exists() and qs[0].items.count() > 0:
            try:
                form = CheckoutForm()
                order = Order.objects.get(user=self.request.user, ordered=False)
                context = {
                    'form': CheckoutForm, 
                    "cart": order, 
                    'couponform':CouponForm,
                    'DISPLAY_COUPON_FORM':True
                }

                shipping_address_qs = Address.objects.filter(
                    user=self.request.user, 
                    address_type='S',
                    default=True
                )
                if shipping_address_qs.exists():
                    context.update({'default_shipping_address': shipping_address_qs[0]})
                
                return render(self.request, "checkout_page.html", context)
            except ObjectDoesNotExist:
                messages.warning(request, "You do not have any active order!")
                return redirect('core:home')
        else:
            messages.warning(request," You do not have any active order!")
            return redirect('core:home')

    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm(self.request.POST or None)
            if form.is_valid():

                # FOR THE SHIPPING ADDRESS
                use_default_shipping = form.cleaned_data['use_default_shipping']

                # To use the shipping address
                if use_default_shipping:
                    address_qs = Address.objects.filter(
                        user=self.request.user, 
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.warning(self.request, "You do not have any default shipping address!")
                        return redirect('core:checkout')
                
                # To add custom/new shipping address
                else:
                    shipping_street_address = form.cleaned_data['shipping_street_address']
                    shipping_apartment_address = form.cleaned_data['shipping_apartment_address']
                    shipping_country = "India"
                    shipping_zip_code = form.cleaned_data['shipping_zip_code']
                    if is_valid_form((shipping_street_address, shipping_country, shipping_zip_code)):
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_street_address,
                            apartment_address = shipping_apartment_address,
                            country = shipping_country,
                            zip_code = shipping_zip_code,
                            address_type="S",
                            default = True,
                        )
                        shipping_address.save()
                    else:
                        messages.info(request, "Please Fill all the required feilds")
                        return redirect('core:checkout')
                order.shipping_address = shipping_address  # save the order
                order.save()  # save the order
                
                # if set_default_shipping is true
                set_default_shipping = form.cleaned_data['set_default_shipping']
                if set_default_shipping:
                    shipping_address.default = True
                    shipping_address.save()
                
                
                
                
                order.save()   # Saving the order


                if form.cleaned_data['payment_method'] == "P":
                    return redirect('core:paypal_payment')
                elif form.cleaned_data['payment_method'] == "S":
                    return redirect('core:stripe_payment')
            messages.warning(self.request, "Failed to Checkout")
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request,"Order Does Not Exist!")
            return redirect('core:order-summary')


class ProductDetail(DetailView):
    model = Item
    template_name = "product_page.html"
    context_object_name = 'product'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user = request.user,
            ordered=False
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,"The Product is Updated to your cart!")
            return redirect('core:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request,"The Product quantity is Added to your cart!")
            return redirect('core:order-summary')
    else:
        order_date = timezone.now() 
        order = Order.objects.create(user=request.user, order_date=order_date)
        order.items.add(order_item)
        messages.info(request,"The Product is Added to your cart!")
        return redirect('core:order-summary')



@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user = request.user,
            ordered=False
        )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                            item=item,
                            user = request.user,
                            ordered=False
                        )[0]
            order.items.remove(order_item)
            
            order_item.delete()
            order.save()
            messages.info(request,"The Product is Removed from your cart!")
            return redirect('core:order-summary')
        else:
            messages.info(request,"The Product was not in your cart!")
            return redirect('core:product-detail', slug=slug)
    else:
        messages.info(request,"You don't have any active order!") 
        return redirect('core:product-detail', slug=slug)



@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("/")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product-detail", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product-detail", slug=slug)


class Search(View):
    paginate_by = 10
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        submit = self.request.GET.get('submit')
        if query is not None:
            lookups = Q(title__icontains=query) | Q(description__icontains=query)
            results= Item.objects.filter(lookups).distinct()
            context = {"results": results,'submitbutton': submit, 'Item':Item.objects.all()}
            return render(request, 'search_result.html', context)
        else:
            return render(request, 'search_result.html',{})


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code = code)
        return coupon

    #TODO: Add except statement for handling errors
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCoupon(View):
    def post(self, request, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                order = Order.objects.get(user=self.request.user, ordered=False)
                code = form.cleaned_data['code']
                order.coupon = get_coupon(request, code)
                order.save()
                
                messages.success(self.request, "Coupon Successfully Applied!")
                return redirect('core:checkout')
            except ObjectDoesNotExist:
                messages.warning(self.request, "You do not have any active order!")
                return redirect('core:checkout')


class AddLenses(View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs['slug']
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user = request.user,
                ordered=False
            )
        order_qs = Order.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            product = order.items.filter(item__slug=item.slug)
            if product.exists():
                context = {
                    "form" : LensesForm(),
                    "product": product[0],
                }
                return render(request, 'lenses_requirements.html', context)
            else:
                messages.info(request,"The Product is not in your cart!")
                return redirect('core:product-detail', slug=slug)
        else:
            messages.info(request,"The Product is not in your cart!")
            return redirect('core:product-detail', slug=slug)
            return redirect('core:order-summary')

    def post(self, request, *args, **kwargs):
        slug = self.kwargs["slug"]
        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
                item=item,
                user = request.user,
                ordered=False
            )
        order_qs = Order.objects.filter(user=request.user, ordered=False)

        if order_qs.exists():
            order = order_qs[0]
            product = order.items.filter(item__slug=item.slug)
            if product.exists():
                product = product[0]
                form = LensesForm(self.request.POST, self.request.FILES)
                if form.is_valid():
                    try:
                        product.lenses_required = True
                        product.lenses = EyeLenses.objects.create(
                            power_type = form.cleaned_data["power_type"],
                            lenses_type = form.cleaned_data["lenses_type"],
                            prescription_image = form.cleaned_data["prescription_image"],
                            user = self.request.user
                        )
                        product.save()
                        messages.info(request,"Success!")
                        return redirect('core:add_lenses', slug=slug)
                    except:
                        messages.info(request,"Exception Occurs!")
                        return redirect('core:add_lenses', slug=slug)
                else:
                    messages.info(request,"else 1!")
                    return redirect('core:add_lenses', slug=slug)
            else:
                messages.info(request,"else 2!")
                return redirect('core:add_lenses', slug=slug)
        else:
            messages.info(request,"else 3!")
            return redirect('core:add_lenses', slug=slug)


class RemoveLenses(View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs["slug"]
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(
            user=self.request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                product = OrderItem.objects.filter(
                    item=item,
                    user=self.request.user,
                    ordered=False
                )[0]
                if product.lenses_required:
                    product.lenses_required = False
                    product.lenses.delete()
                    product.lenses = None
                    product.save()                 
                    messages.info(request,"Successully Removed the Lenses")
                    return redirect("core:add_lenses", slug=slug)
                else:
                    messages.info(request,"You don't have attached Lenses to this product")
                    return redirect("core:add_lenses", slug=slug)
            else:
                messages.info(request,"Can't Find this Product in your cart")
                return redirect("core:order-summary")

        else:
            messages.info(request,"Your Cart seems to be empty")
            return redirect("core:home")





            


@csrf_exempt
def payment_done(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
    except Order.DoesNotExist:
        messages.error(request, "No pending order found.")
        return redirect("core:order-summary")  # Redirect to cart or order summary page

    order_item = order.items.all()
    order_item.update(ordered=True)
    
    for item in order_item:
        item.save()

    # Create a payment record
    payment_receipt = Payment.objects.create(
        user=request.user,
        amount=order.get_total_bill_amount_with_discount(),
        transaction_id=order.id
    )
    payment_receipt.save()

    # Update order details
    order.ordered = True
    order.ref_code = create_ref_code()
    order.payment = payment_receipt
    order.save()

    messages.success(request, "Order successfully completed!")
    return redirect("core:home") 


@csrf_exempt
def payment_canceled(request):
    messages.info(request,"Order Cancelled!")
    return redirect("core:checkout")

import logging

# Set up logging
logger = logging.getLogger(__name__)

# Make sure to set your Stripe API key in settings.py and import it
# or set it here directly for testing
from django.conf import settings
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'your_test_key_here')  # Fallback for testing

class StripePayment(View):
    def get(self, request, *args, **kwargs):
        try:
            # Log the user to help debug
            logger.info(f"Processing payment for user: {request.user}")
            
            # Check if the user is authenticated
            if not request.user.is_authenticated:
                messages.error(request, "Please log in to continue")
                return redirect("account_login")
                
            # Fetch the order
            order = Order.objects.get(user=request.user, ordered=False)
            logger.info(f"Found order: {order.id} with total: {order.get_total_bill_amount_with_discount()}")
            
            # For testing, use a simple approach first
            context = {
                'order': order,
                'cart': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_sample'),
            }
            
            return render(request, "stripe_payment.html", context)
            
        except Order.DoesNotExist:
            logger.error(f"No active order found for user: {request.user}")
            messages.error(request, "You don't have an active order")
            return redirect("core:checkout")
        except Exception as e:
            logger.error(f"Error in stripe payment get: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("core:checkout")

    def post(self, request, *args, **kwargs):
        try:
            logger.info("Processing payment post request")
            token = request.POST.get('stripeToken')
            logger.info(f"Received token: {token}")
            
            if not token:
                messages.error(request, "No payment token received")
                return redirect('core:stripe_payment')
                
            order = Order.objects.get(user=request.user, ordered=False)
            
            # Just for testing - log but don't process
            logger.info(f"Would charge {order.get_total_bill_amount_with_discount()} INR")
            
            # For simplicity during debugging, skip the actual charge
            # Just mark the order as paid
            order.ordered = True
            order.save()
            
            messages.success(request, "Your payment was successful!")
            return redirect('core:payment_done')
                
        except Exception as e:
            logger.error(f"Error in stripe payment post: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('core:checkout')




class RefundRequest(View):
    def get(self, request, *args, **kwargs):
        form = RefundForm()
        context = {
            "form": form,
        }
        return render(self.request, "request_refund.html", context)

    def post(self, request, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            ref_code = form.cleaned_data["ref_code"]

            try:
                order = Order.objects.get(ref_code=ref_code)
                if order.refund_granted == False and order.refund_request == False:
                    order.refund_request = True
                    order.save()

                    refund = Refund.objects.create(
                        order=order,
                        message = message,
                        email=email,
                    )
                    refund.save()
                    
                    messages.info(self.request, "Request for refund is Successfull.")
                    return redirect("core:refund_request")
                    
                elif order.refund_granted == False and order.refund_request == True:                 
                    messages.info(self.request, "Please wait your request in pending this order.")
                    return redirect("core:refund_request")

                elif order.refund_granted == True and order.refund_request == False:
                    messages.info(self.request, "Refund for this order has been already granted!")
                    return redirect("core:refund_request")
                    
                    
                else :
                    messages.info(self.request, "We are running with issues in processing refund for this order! Please try again later!")
                    return redirect("core:refund_request")
                    
            except ObjectDoesNotExist:
                messages.warning(self.request, "Order does not exist! Please enter correct Order Referral Code.")
                return redirect("core:refund_request")
        
        messages.warning(self.request, "Please enter the valid Information!")
        return redirect("core:refund_request")

class UserProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            user_profile = None  # Or create one dynamically if needed

        orders = Order.objects.filter(user=self.request.user, ordered=True)

        context = {
            "user_profile": user_profile,
            "orders": orders,
        }
        return render(request, "user_profile.html", context)



   