from rest_framework import serializers
from .models import MenuItem, Category, Cart, OrderItem, Order
from django.contrib.auth.models import User, Group


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        many=False, slug_field='slug', queryset=Category.objects.all())
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']


class UserSerializer(serializers.ModelSerializer):

    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'date_joined', 'groups']


class CartSerializer(serializers.ModelSerializer):

    menuitem = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all())

    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity']

    def create(self, validated_data):
        unit_price = validated_data['menuitem'].price
        price = validated_data['quantity'] * unit_price
        data_dict = dict(validated_data)
        data_dict['unit_price'] = unit_price
        data_dict['price'] = price
        return Cart.objects.create(**data_dict)


class CartSerializer2(serializers.ModelSerializer):

    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'unit_price', 'price']


class OrderItemSerializer(serializers.ModelSerializer):

    menuitem = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderItemSerializer2(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):

    delivery_crew = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    class Meta:
        model = Order
        fields = ['delivery_crew', 'status', 'total', 'date']


class OrderSerializer2(serializers.ModelSerializer):

    delivery_crew = UserSerializer(read_only=True)
    items = OrderItemSerializer2(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total', 'date', 'delivery_crew', 'items']
