from rest_framework import serializers

from .models import Product,Collection

from decimal import Decimal

class CollectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)

class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=6, decimal_places=2,source='unit_price')
    price_with_tax = serializers.SerializerMethodField()

    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collection-detail',
    )

    def get_price_with_tax(self,product):
        return product.unit_price * Decimal(1.1)