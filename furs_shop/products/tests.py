from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
from .models import Product, Category


class ProductListViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1")
        Product.objects.create(name="Product 1", price=10.00, specifications={}, category=self.category)
        Product.objects.create(name="Product 2", price=20.00, specifications={}, category=self.category)

    def test_product_list_view_status_code(self):
        """Проверяем, что страница доступна и возвращает статус 200"""
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_view_template_used(self):
        """Проверяем, что используется правильный шаблон"""
        response = self.client.get(reverse('product_list'))
        self.assertTemplateUsed(response, 'products/product_list.html')

    def test_product_list_view_content(self):
        """Проверяем, что на странице отображаются продукты"""
        response = self.client.get(reverse('product_list'))
        self.assertContains(response, "Product 1")
        self.assertContains(response, "Product 2")
        self.assertEqual(len(response.context['products']), 2)


class ProductListViewAPITest(APITestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name="Category 1")
        self.category2 = Category.objects.create(name="Category 2")

        self.product1 = Product.objects.create(name="Product 1", price=10.00, specifications={}, category=self.category1)
        self.product2 = Product.objects.create(name="Product 2", price=20.00, specifications={}, category=self.category2)

    def test_list_products(self):
        """Проверяем, что список продуктов возвращается корректно"""
        url = reverse('product-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_products_by_category(self):
        """Проверяем фильтрацию продуктов по категории"""
        url = reverse('product-list') + f'?category={self.category1.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Product 1')

    def test_ordering_products_by_price(self):
        """Проверяем сортировку продуктов по цене"""
        url = reverse('product-list') + '?ordering=price'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'Product 1')
        self.assertEqual(response.data[1]['name'], 'Product 2')


class ProductDetailViewAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Category 1")
        self.product = Product.objects.create(name="Product 1", price=10.00, specifications={}, category=self.category)

    def test_retrieve_product(self):
        """Проверяем получение деталей продукта"""
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Product 1')
        self.assertEqual(response.data['price'], '10.00')

    def test_retrieve_nonexistent_product(self):
        """Проверяем получение несуществующего продукта"""
        url = reverse('product-detail', args=[999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryListViewAPITest(APITestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name="Parent Category 1")
        self.category2 = Category.objects.create(name="Parent Category 2")
        self.sub_category = Category.objects.create(name="Sub Category", parent=self.category1)

    def test_list_top_level_categories(self):
        """Проверяем, что список родительских категорий возвращается корректно"""
        url = reverse('category-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Parent Category 1')
        self.assertEqual(response.data[1]['name'], 'Parent Category 2')
