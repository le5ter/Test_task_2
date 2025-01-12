from django.shortcuts import redirect, render
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')

    product = Product.objects.get(id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('product_list')


def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart, created = Cart.objects.get_or_create(user=request.user)
    total_price = cart.get_total_price()
    return render(request, 'cart/view_cart.html', {'cart': cart, 'total_price': total_price})


def checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')

    cart, created = Cart.objects.get_or_create(user=request.user)

    if not cart.items.all():
        return redirect('view_cart')

    order = Order.objects.create(user=request.user, total_price=0)
    total_price = 0

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price * item.quantity
        )
        total_price += item.product.price * item.quantity

    order.total_price = total_price
    order.save()

    cart.items.all().delete()

    return render(request, 'cart/order_success.html', {'order': order})
