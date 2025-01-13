from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product, Category


class CartViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.category = Category.objects.create(name="Category 1")
        self.product1 = Product.objects.create(name="Product 1", price=100.00, specifications={}, category=self.category)
        self.product2 = Product.objects.create(name="Product 2", price=200.00, specifications={}, category=self.category)

    def test_add_to_cart_unauthenticated(self):
        """Неаутентифицированный пользователь должен быть перенаправлен на страницу входа"""
        url = reverse('add_to_cart', args=[self.product1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_add_to_cart_authenticated(self):
        """Проверяем добавление товара в корзину аутентифицированным пользователем"""
        self.client.login(username='testuser', password='testpassword')

        url = reverse('add_to_cart', args=[self.product1.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('product_list'))

        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, product=self.product1)

        self.assertEqual(cart_item.quantity, 1)

    def test_view_cart_unauthenticated(self):
        """Неаутентифицированный пользователь должен быть перенаправлен на страницу входа при просмотре корзины"""
        url = reverse('view_cart')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_view_cart_authenticated(self):
        """Проверяем просмотр корзины аутентифицированным пользователем"""
        self.client.login(username='testuser', password='testpassword')

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)

        url = reverse('view_cart')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/view_cart.html')

        self.assertEqual(response.context['cart'], cart)
        self.assertEqual(response.context['total_price'], 200.00)

    def test_checkout_empty_cart(self):
        """Проверяем редирект на корзину, если она пуста при оформлении заказа"""
        self.client.login(username='testuser', password='testpassword')

        url = reverse('checkout')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('view_cart'))

    def test_checkout_with_items(self):
        """Проверяем оформление заказа с товарами в корзине"""
        self.client.login(username='testuser', password='testpassword')

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)

        url = reverse('checkout')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/order_success.html')

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_price, 200.00)

        order_item = OrderItem.objects.get(order=order, product=self.product1)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, 200.00)

        self.assertFalse(cart.items.exists())


class CartViewAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.category = Category.objects.create(name="Category 1")
        self.product1 = Product.objects.create(name="Product 1", specifications={}, price=100.00, category=self.category)
        self.product2 = Product.objects.create(name="Product 2", specifications={}, price=200.00, category=self.category)

        self.cart_url = reverse('cart')

    def get_jwt_token(self):
        """Получаем JWT токен для аутентифицированного пользователя"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        return response.data['access']

    def test_get_cart_unauthenticated(self):
        """Неаутентифицированный пользователь должен получить 401 Unauthorized"""
        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_cart_authenticated(self):
        """Проверяем получение корзины для аутентифицированного пользователя"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)

        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['product']['name'], 'Product 1')
        self.assertEqual(response.data['items'][0]['quantity'], 2)

    def test_post_add_to_cart(self):
        """Проверяем добавление товара в корзину"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        data = {'product_id': self.product1.id}
        response = self.client.post(self.cart_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Product added to cart')

        cart = Cart.objects.get(user=self.user)
        cart_item = CartItem.objects.get(cart=cart, product=self.product1)

        self.assertEqual(cart_item.quantity, 2)

    def test_put_update_cart_item(self):
        """Проверяем обновление количества товара в корзине"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)

        data = {'product_id': self.product1.id, 'quantity': 5}
        response = self.client.put(self.cart_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Cart item updated')

        cart_item = CartItem.objects.get(cart=cart, product=self.product1)
        self.assertEqual(cart_item.quantity, 5)

    def test_delete_cart_item(self):
        """Проверяем удаление товара из корзины"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product1, quantity=2)

        data = {'product_id': self.product1.id}
        response = self.client.delete(self.cart_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Cart item removed')

        self.assertFalse(CartItem.objects.filter(cart=cart, product=self.product1).exists())


class OrderCreateViewAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        self.category = Category.objects.create(name="Category 1")
        self.product = Product.objects.create(name="Product 1", specifications={}, price=100.00, category=self.category)

        self.order_url = reverse('order-create')

    def get_jwt_token(self):
        """Получаем JWT токен для аутентифицированного пользователя"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        return response.data['access']

    def test_order_creation_with_empty_cart(self):
        """Проверяем, что невозможно оформить заказ с пустой корзиной"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        Cart.objects.create(user=self.user)
        response = self.client.post(self.order_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Cart is empty')

    def test_order_creation_with_items(self):
        """Проверяем успешное оформление заказа"""
        token = self.get_jwt_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)

        response = self.client.post(self.order_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Order created successfully')

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total_price, 300.00)

        order_item = OrderItem.objects.get(order=order, product=self.product)
        self.assertEqual(order_item.quantity, 3)
        self.assertEqual(order_item.price, 300.00)

        self.assertFalse(cart.items.exists())
