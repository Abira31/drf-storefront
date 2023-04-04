from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView,
                                    RetrieveUpdateDestroyAPIView)
from rest_framework import viewsets

from .serializers import (ProductSerializer,
                        CollectionSerializer,
                        ReviewSerializer)

from .models import Product,Collection,Review


class ProducViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.only('id','title','description','slug','inventory','unit_price','collection').all()\
        .prefetch_related('collection')   

class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.only('id','title').all()

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.only('id','data','name','description').filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
