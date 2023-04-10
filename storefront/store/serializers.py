from rest_framework import serializers
from django.db import transaction

from .models import (Product,Collection,
                    Review,Cart,
                    CartItem,
                    Customer,
                    Order,
                    OrderItem,
                    ProductImage)

from decimal import Decimal

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('id', 'title')

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id','image')

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id,**validated_data)

class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True,read_only=True)
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection-detail'
    # )

    def get_price_with_tax(self,product):
        return product.unit_price * Decimal(1.1)
    class Meta:
        model = Product
        fields = ('id','title','description','slug','inventory',
                  'unit_price','price_with_tax','collection','images')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id','data','name','description')

    def create(self,validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(**validated_data,product_id=product_id)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id','title','unit_price')

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    
    def get_total_price(self,cart_item):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ('id','product','quantity','total_price')

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cart):
        return sum([cart_item.quantity * cart_item.product.unit_price for cart_item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ('id','items','total_price')   

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ('id','product_id','quantity')

    def save(self, *args, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        cart_item,created = CartItem.objects.get_or_create(cart_id=cart_id, product_id=product_id)
        cart_item.quantity += quantity
        cart_item.save()
        return cart_item

    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Not product with id')
        return value

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ('id','user_id','phone','birth_date','membership')

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        models = CartItem
        fields = ('quantity',)

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id','customer','placed_at', 'payment_status', 'items']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('payment_status',)

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self,value):
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Not cart with id')
        if CartItem.objects.filter(cart_id=value).count() > 0:
            raise serializers.ValidationError('The cart is empty')
        return value

    def save(self,*args,**kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer = Customer.objects.get(
                user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()
            return order

