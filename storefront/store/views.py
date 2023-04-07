from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (ListCreateAPIView,
                                    RetrieveUpdateDestroyAPIView)
from rest_framework import viewsets,mixins
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum,F
from django.shortcuts import get_object_or_404

from .serializers import (ProductSerializer,
                        CollectionSerializer,
                        ReviewSerializer,
                        CartSerializer,
                        CartItemSerializer,
                        AddCartItemSerializer,
                        CustomerSerializer)

from .models import (Product,Collection,
                    Review,Cart,
                    CartItem,Customer)
from .filters import ProductFilter
from .pagination import DefaultPagination

class ProducViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.only('id','title','description','slug','inventory','unit_price','collection').all()\
        .select_related('collection')
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

class CartViewSet(mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                viewsets.GenericViewSet):
    queryset = Cart.objects.all().select_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','post','delete','patch']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        cart_pk = self.kwargs['cart_pk']
        return CartItem.objects\
            .filter(cart_id=cart_pk)\
            .select_related('product').only('id','product__id','product__title','product__unit_price','quantity')
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

class CustomerViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

    @action(detail=False,methods=['get','put'])
    def me(self,request):
        if request.user.is_authenticated:
            customer = get_object_or_404(Customer,user_id=request.user.id)
            if request.method == 'GET':
                serializer = CustomerSerializer(customer)
            else:
                serializer = CustomerSerializer(customer,data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
        
