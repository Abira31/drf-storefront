from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from .serializers import ProductSerializer,CollectionSerializer

from .models import Product,Collection

@api_view()
def product_list(request):
    queryset = Product.objects.only('id', 'title', 'unit_price','collection').all()\
        .prefetch_related('collection')
    serializer = ProductSerializer(queryset, many=True,context={'request': request})
    return Response(serializer.data)


@api_view()
def product_detail(request, pk):
    product = Product.objects.only('id','title','unit_price')
    product = get_object_or_404(product, pk=pk)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view()
def collection_detail(request, pk):
    
    collection = Collection.objects.only('id','title')
    collection = get_object_or_404(collection, pk=pk)
    serializer = CollectionSerializer(collection)
    return Response(serializer.data)