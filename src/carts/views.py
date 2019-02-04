from django.shortcuts import render, redirect

from products.models import Product
from product_quantities.models import ProductQuantity
from .models import Cart
from .forms import CartForm
from orders.models import Order


def cart_home(request):
    form = CartForm()
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    context = {
        'form': form,
        'cart': cart_obj,
    }
    return render(request, 'carts/home.html', context)


def cart_add(request):
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return redirect('cart:home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj not in cart_obj.products.all():
            cart_obj.products.add(product_obj)
            ProductQuantity.objects.new(cart_obj, product_obj)
        quant_obj = ProductQuantity.objects.get_queryset().exist(cart_obj, product_obj)
        print(quant_obj.quantity)
        request.session['cart_items'] = cart_obj.products.count()
    return redirect('cart:home')


def cart_remove(request):
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return redirect('cart:home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
        request.session['cart_items'] = cart_obj.products.count()
    return redirect('cart:home')


def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect('cart:home')
    else:
        order_obj, new_order_obj = Order.objects.get_or_create(cart=cart_obj)
    return render(request, 'carts/checkout.html', {'object': order_obj})
