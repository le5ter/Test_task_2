from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer
from products.models import Product


class CartView(APIView):
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        product = Product.objects.get(id=product_id)
        cart_item, _ = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        return Response({'message': 'Product added to cart'}, status=status.HTTP_201_CREATED)

    def put(self, request):
        cart = Cart.objects.get(user=request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.quantity = quantity
        cart_item.save()
        return Response({'message': 'Cart item updated'})

    def delete(self, request):
        cart = Cart.objects.get(user=request.user)
        product_id = request.data.get('product_id')
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
        return Response({'message': 'Cart item removed'})


class OrderCreateView(APIView):
    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'message': 'Order created successfully'}, status=status.HTTP_201_CREATED)
