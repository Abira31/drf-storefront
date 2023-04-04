from rest_framework import serializers

from .models import Product,Collection,Review

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