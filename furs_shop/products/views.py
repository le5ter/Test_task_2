from .models import Product
from django.shortcuts import render


def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})
