from django.contrib.auth.models import User
from rest_framework import serializers
from .models import MenuItem, Category, Order, Cart, OrderItem


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']


class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price',
                  'category', 'featured', 'category_id']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew',
                  'status', 'total', 'date']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'menuitem', 'quantity', 'unit_price', 'price'
        ]


# from rest_framework import serializers
# from django.contrib.auth.models import User
# from decimal import Decimal

# from .models import Category, MenuItem, Cart, Order, OrderItem


# class CategorySerializer (serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'title', 'slug']


# class MenuItemSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(
#         queryset=Category.objects.all()
#     )
#     # category = CategorySerializer(read_only=True)
#     class Meta:
#         model = MenuItem
#         fields = ['id', 'title', 'price', 'category', 'featured']


# class CartSerializer(serializers.ModelSerializer):
#     user = serializers.PrimaryKeyRelatedField(
#         queryset=User.objects.all(),
#         default=serializers.CurrentUserDefault()
#     )


#     def validate(self, attrs):
#         attrs['price'] = attrs['quantity'] * attrs['unit_price']
#         return attrs

#     class Meta:
#         model = Cart
#         fields = ['user', 'menuitem', 'unit_price', 'quantity', 'price']
#         extra_kwargs = {
#             'price': {'read_only': True}
#         }


# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['order', 'menuitem', 'quantity', 'price']


# class OrderSerializer(serializers.ModelSerializer):

#     orderitem = OrderItemSerializer(many=True, read_only=True, source='order')

#     class Meta:
#         model = Order
#         fields = ['id', 'user', 'delivery_crew',
#                   'status', 'date', 'total', 'orderitem']


# class UserSerilializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id','username','email']
