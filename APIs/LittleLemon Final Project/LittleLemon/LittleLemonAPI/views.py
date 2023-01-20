from django.shortcuts import render, get_object_or_404
from django.core import serializers
from rest_framework import generics, status
from rest_framework.response import Response
import datetime

from rest_framework.decorators import throttle_classes, api_view, permission_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permissions import IsCustomerOrDeliveryCrew

from django.contrib.auth.models import User, Group
from .serializer import UserSerializer, MenuItemSerializer, OrderSerializer, CartSerializer, OrderItemSerializer
from .models import MenuItem, Category, Order, Cart, OrderItem
from django.core.paginator import Paginator, EmptyPage

# USERS


@permission_classes([IsAuthenticated])
class Users(generics.CreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.all()
    serializer_class = UserSerializer


@permission_classes([IsAuthenticated])
class UserDetail(generics.ListAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.all()
    serializer_class = UserSerializer

# MENU ITEMS


@permission_classes([IsAuthenticated])
class MenuItemsList(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category__title']


@permission_classes([IsAuthenticated, IsCustomerOrDeliveryCrew])
class MenuItem(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

# ORDER LIST


@api_view(['GET', 'POST'])
def orderlist(request):
    if (request.user.groups.filter(name='Customer').exists()):
        if request.method == 'GET':
            user = request.user
            orders = Order.objects.filter(user=user)
            data = []
            for id in orders:
                itemOrder = OrderItem.objects.filter(order=id).first()

                if itemOrder != None:
                    data.append(itemOrder)

            orderitems = OrderItemSerializer(data, many=True)

            return Response(orderitems.data, 200)

        if request.method == 'POST':
            user = request.user
            #  gets current cart
            currentcart = Cart.objects.filter(user=user)

            for cart in currentcart:
                total = cart.unit_price * cart.price
                menuitem = cart.menuitem
                quantity = cart.quantity
                unit_price = cart.unit_price
                price = cart.price

            # creates a new order
                neworder = Order(user=user, total=total,
                                 date=datetime.date.today())
                neworder.save()
                # adds cart items to order items table
                orderItem = OrderItem(
                    order=neworder, menuitem=menuitem, quantity=quantity, unit_price=unit_price, price=price)
                orderItem.save()
                cart.delete()
            return Response({"message": "Order item created"}, 201)
    elif (request.user.groups.filter(name='Manager').exists()):
        if request.method == 'GET':
            orders = Order.objects.select_related('user').all()
            username = request.query_params.get('username')
            perPage = request.query_params.get('perpage', default=10)
            page = request.query_params.get('page', default=1)
            if username:
                orders = orders.filter(user__username=username)
            data = []
            for id in orders:
                itemOrder = OrderItem.objects.filter(order=id).first()

                if itemOrder != None:
                    data.append(itemOrder)

            paginator = Paginator(data, per_page=perPage)
            try:
                data = paginator.page(number=page)
            except EmptyPage:
                data = []
            orderitems = OrderItemSerializer(data, many=True)

            return Response(orderitems.data, 200)
    elif (request.user.groups.filter(name='Delivery Crew').exists()):
        if request.method == 'GET':
            orders = Order.objects.filter(delivery_crew=request.user)
            serializer = OrderSerializer(orders, many=True)
            print(orders, "orders from delivery")
            return Response(serializer.data, 200)

    else:
        return Response({"message": "You are not authorized"}, 403)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def orderDetail(request, pk=None):

    if (request.user.groups.filter(name='Customer').exists()):
        if request.method == 'GET':
            order = Order.objects.filter(pk=pk).filter(
                user=request.user).first()
            orderitem = OrderItem.objects.filter(order=order.id)
            serialized = OrderItemSerializer(orderitem, many=True)
            return Response(serialized.data, 200)
    elif (request.user.groups.filter(name='Manager').exists()):
        if request.method == 'PUT':
            order = Order.objects.get(pk=pk)
            delivery_crew = request.data.getlist('delivery_crew')
            status = request.data.getlist('status')
            deliverycrew = User.objects.get(pk=delivery_crew[0])
            order.delivery_crew = deliverycrew
            order.status = status[0]
            order.save()
            return Response({"message: Order updated"}, 200)
        if request.method == 'DELETE':
            order = Order.objects.filter(pk=pk).delete()
            return Response({"message: Order deleted"}, 200)
    elif (request.user.groups.filter(name='Delivery Crew').exists()):
        if request.method == 'PATCH':
            order = Order.objects.get(pk=pk)
            status = request.data.getlist('status')
            order.status = status[0]
            order.save()
            return Response({"Message": "Status updated"}, 200)
    else:
        return Response({"message": "You are not authorized"}, 403)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cartList(request):
    if request.user.groups.filter(name='Customer').exists():
        if request.method == 'GET':
            cartItems = Cart.objects.filter(user=request.user)
            serialized_cart = CartSerializer(cartItems, many=True)
            return Response(serialized_cart.data, 200)
        if request.method == 'POST':
            serialized_cart_item = CartSerializer(
                data=request.data, many=True)
            serialized_cart_item.is_valid(raise_exception=True)
            serialized_cart_item.save(user=request.user)
            return Response(data=request.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            cartItems = Cart.objects.filter(user=request.user)
            cartItems.delete()
            return Response({"message": "menu items removed"}, 200)
    else:
        return Response({"message": "You are not authorized"}, 403)


@api_view()
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# USER GRUOPS
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def managers(request, pk=None):
    if request.user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            users = User.objects.filter(groups__id=1)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name="Manager")
                if request.method == 'POST':
                    managers.user_set.add(user)

                return Response({"message": "user added to the manager group"}, status.HTTP_201_CREATED)
            return Response({"message": "Error"}, status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "You are not authorized"}, 403)


@ api_view(['DELETE'])
@ permission_classes([IsAuthenticated])
def deleteUserfromGroup(request, pk=None):
    if request.user.groups.filter(name='Manager').exists():
        user = User.objects.get(pk=pk)
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)
        return Response({"message": "user removed from the manager group"}, status.HTTP_200_OK)
    else:
        return Response({"message": "You are not authorized"}, 403)


@ api_view(['GET', 'POST'])
def deliveryCrew(request):

    if request.user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            users = User.objects.filter(groups__id=3)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, 200)
        else:
            username = request.data['username']
            if username:
                user = get_object_or_404(User, username=username)
                deliverycrew = Group.objects.get(name="Delivery Crew")
                if request.method == 'POST':
                    deliverycrew.user_set.add(user)
                    return Response({"message": "user added to the delivery group"}, status.HTTP_201_CREATED)
            return Response({"message": "Error"}, status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"message": "You are not authorized"}, 403)


@ api_view(['DELETE'])
@ permission_classes([IsAuthenticated])
def deleteUserfromDeliveryGroup(request, pk=None):
    if request.user.groups.filter(name='Manager').exists():
        user = User.objects.get(pk=pk)
        deliverycrew = Group.objects.get(name="Delivery Crew")
        deliverycrew.user_set.remove(user)
        return Response({"message": "user removed from the manager group"}, status.HTTP_200_OK)
    else:
        return Response({"message": "You are not authorized"}, 403)


# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
# from .models import Category, MenuItem, Cart, Order, OrderItem
# from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, UserSerilializer
# from rest_framework.response import Response

# from rest_framework.permissions import IsAdminUser
# from django.shortcuts import  get_object_or_404

# from django.contrib.auth.models import Group, User

# from rest_framework import viewsets
# from rest_framework import status


# class CategoriesView(generics.ListCreateAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer

#     def get_permissions(self):
#         permission_classes = []
#         if self.request.method != 'GET':
#             permission_classes = [IsAuthenticated]

#         return [permission() for permission in permission_classes]

# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     search_fields = ['category__title']
#     ordering_fields = ['price', 'inventory']

#     def get_permissions(self):
#         permission_classes = []
#         if self.request.method != 'GET':
#             permission_classes = [IsAuthenticated]

#         return [permission() for permission in permission_classes]
# class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer

#     def get_permissions(self):
#         permission_classes = []
#         if self.request.method != 'GET':
#             permission_classes = [IsAuthenticated]

#         return [permission() for permission in permission_classes]

# class CartView(generics.ListCreateAPIView):
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Cart.objects.all().filter(user=self.request.user)

#     def delete(self, request, *args, **kwargs):
#         Cart.objects.all().filter(user=self.request.user).delete()
#         return Response("ok")


# class OrderView(generics.ListCreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         if self.request.user.is_superuser:
#             return Order.objects.all()
#         elif self.request.user.groups.count()==0: #normal customer - no group
#             return Order.objects.all().filter(user=self.request.user)
#         elif self.request.user.groups.filter(name='Delivery Crew').exists(): #delivery crew
#             return Order.objects.all().filter(delivery_crew=self.request.user)  #only show oreders assigned to him
#         else: #delivery crew or manager
#             return Order.objects.all()
#         # else:
#         #     return Order.objects.all()

#     def create(self, request, *args, **kwargs):
#         menuitem_count = Cart.objects.all().filter(user=self.request.user).count()
#         if menuitem_count == 0:
#             return Response({"message:": "no item in cart"})

#         data = request.data.copy()
#         total = self.get_total_price(self.request.user)
#         data['total'] = total
#         data['user'] = self.request.user.id
#         order_serializer = OrderSerializer(data=data)
#         if (order_serializer.is_valid()):
#             order = order_serializer.save()

#             items = Cart.objects.all().filter(user=self.request.user).all()

#             for item in items.values():
#                 orderitem = OrderItem(
#                     order=order,
#                     menuitem_id=item['menuitem_id'],
#                     price=item['price'],
#                     quantity=item['quantity'],
#                 )
#                 orderitem.save()

#             Cart.objects.all().filter(user=self.request.user).delete() #Delete cart items

#             result = order_serializer.data.copy()
#             result['total'] = total
#             return Response(order_serializer.data)

#     def get_total_price(self, user):
#         total = 0
#         items = Cart.objects.all().filter(user=user).all()
#         for item in items.values():
#             total += item['price']
#         return total


# class SingleOrderView(generics.RetrieveUpdateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def update(self, request, *args, **kwargs):
#         if self.request.user.groups.count()==0: # Normal user, not belonging to any group = Customer
#             return Response('Not Ok')
#         else: #everyone else - Super Admin, Manager and Delivery Crew
#             return super().update(request, *args, **kwargs)


# class GroupViewSet(viewsets.ViewSet):
#     permission_classes = [IsAdminUser]
#     def list(self, request):
#         users = User.objects.all().filter(groups__name='Manager')
#         items = UserSerilializer(users, many=True)
#         return Response(items.data)

#     def create(self, request):
#         user = get_object_or_404(User, username=request.data['username'])
#         managers = Group.objects.get(name="Manager")
#         managers.user_set.add(user)
#         return Response({"message": "user added to the manager group"}, 200)

#     def destroy(self, request):
#         user = get_object_or_404(User, username=request.data['username'])
#         managers = Group.objects.get(name="Manager")
#         managers.user_set.remove(user)
#         return Response({"message": "user removed from the manager group"}, 200)

# class DeliveryCrewViewSet(viewsets.ViewSet):
#     permission_classes = [IsAuthenticated]
#     def list(self, request):
#         users = User.objects.all().filter(groups__name='Delivery Crew')
#         items = UserSerilializer(users, many=True)
#         return Response(items.data)

#     def create(self, request):
#         #only for super admin and managers
#         if self.request.user.is_superuser == False:
#             if self.request.user.groups.filter(name='Manager').exists() == False:
#                 return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)

#         user = get_object_or_404(User, username=request.data['username'])
#         dc = Group.objects.get(name="Delivery Crew")
#         dc.user_set.add(user)
#         return Response({"message": "user added to the delivery crew group"}, 200)

#     def destroy(self, request):
#         #only for super admin and managers
#         if self.request.user.is_superuser == False:
#             if self.request.user.groups.filter(name='Manager').exists() == False:
#                 return Response({"message":"forbidden"}, status.HTTP_403_FORBIDDEN)
#         user = get_object_or_404(User, username=request.data['username'])
#         dc = Group.objects.get(name="Delivery Crew")
#         dc.user_set.remove(user)
#         return Response({"message": "user removed from the delivery crew group"}, 200)
