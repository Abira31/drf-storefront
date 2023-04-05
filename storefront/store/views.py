from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView,
                                    RetrieveUpdateDestroyAPIView)
from rest_framework import viewsets
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (ProductSerializer,
                        CollectionSerializer,
                        ReviewSerializer)

from .models import Product,Collection,Review
from .filters import ProductFilter
from .pagination import DefaultPagination

class ProducViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.only('id','title','description','slug','inventory','unit_price','collection').all()\
        .prefetch_related('collection')
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_updated']

class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.only('id','title').all()

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.only('id','data','name','description').filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
