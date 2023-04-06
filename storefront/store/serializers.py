from rest_framework import serializers

from .models import (Product,Collection,
                    Review,Cart,
                    CartItem)

from decimal import Decimal

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ('id', 'title')

class ProductSerializer(serializers.ModelSerializer):  
    price_with_tax = serializers.SerializerMethodField()

    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection-detail'
    # )

    def get_price_with_tax(self,product):
        return product.unit_price * Decimal(1.1)
    class Meta:
        model = Product
        fields = ('id','title','description','slug','inventory','unit_price','price_with_tax','collection')


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

