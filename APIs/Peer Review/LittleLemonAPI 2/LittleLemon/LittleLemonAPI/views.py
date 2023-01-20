from django.shortcuts import render, get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .models import MenuItem, Cart, Order, OrderItem, Category
from .permissions import ManagerWriteOnlyPermission, ManagerOnlyPermission
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, CartSerializer2,  OrderSerializer, OrderSerializer2, CategorySerializer
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

class CategoryItemViewMultiple(ListCreateAPIView):
    queryset = Category.objects.all()
    permission_classes = [ManagerWriteOnlyPermission,]
    serializer_class = CategorySerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

class MenuItemsViewMultiple(ListCreateAPIView):
    permission_classes = [ManagerWriteOnlyPermission,]
    serializer_class = MenuItemSerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    def get_queryset(self):
        myset = MenuItem.objects.all()

        perpage = self.request.query_params.get('perpage', 3)
        page = self.request.query_params.get('page',1)

        if self.request.query_params.get('search'):
            myset = myset.filter(title__icontains = self.request.query_params.get('search'))

        if self.request.query_params.get('name'):
            myset = myset.filter(title = self.request.query_params.get('name'))

        if self.request.query_params.get('category'):
            myset = myset.filter(category__slug = self.request.query_params.get('category'))

        if self.request.query_params.get('featured'):
            myset = myset.filter(featured = self.request.query_params.get('featured'))

        if self.request.query_params.get('low_price'):
            myset = myset.filter(price__gte = float(self.request.query_params.get('low_price')))

        if self.request.query_params.get('high_price'):
            myset = myset.filter(price__lte = float(self.request.query_params.get('high_price')))

        if self.request.query_params.get('order_by'):
            order_by = self.request.query_params.get('order_by')
            ordering_fields = order_by.split(",")
            myset = myset.order_by(*ordering_fields)


        paginator = Paginator(myset, per_page=perpage)
        try:
            myset = paginator.page(number=page)
        except EmptyPage:
            myset = []

        return myset


class MenuItemsViewSingle(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    permission_classes = [ManagerWriteOnlyPermission,]
    serializer_class = MenuItemSerializer
    lookup_url_kwarg = 'menuItem'
    throttle_classes = [UserRateThrottle, AnonRateThrottle]


class GenericGroupManager(APIView):
    permission_classes = [ManagerOnlyPermission,]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]


    def get_target_group_name(self):
        return ""

    def get(self, request, userId = None, *args, **kwargs):
        if userId is not None:
            return Response(status=500)

        myusers = User.objects.filter(groups__name=self.get_target_group_name())

        my_serialized_users = UserSerializer(myusers, many=True)

        return Response(my_serialized_users.data, 200)

    def post(self, request, userId = None, *args, **kwargs):

        if userId is not None:
            return Response(status=500)

        username = request.data.get("username")

        if username is None:
            return Response({'message':'Invalid user name specified'}, 404)

        promoted_user = get_object_or_404(User, username = request.data.get("username"))
        target_group = get_object_or_404(Group, name=self.get_target_group_name())
        target_group.user_set.add(promoted_user)
        return Response(status=201)

    def delete(self, request, userId = None, *args, **kwargs):
      
        demoted_user = get_object_or_404(User, id=userId)
        target_group = get_object_or_404(Group, name=self.get_target_group_name())
        target_group.user_set.remove(demoted_user)
        return Response(status=200)


class ManagerGroupView(GenericGroupManager):

    def get_target_group_name(self):
        return "Manager"

class DeliveryCrewGroupView(GenericGroupManager):

    def get_target_group_name(self):
        return "Delivery Crew"

class CartManagementView(APIView):

    permission_classes = [IsAuthenticated,]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    
    def get(self, request, *args, **kwargs):

        userCart = Cart.objects.filter(user = request.user)

        perpage = self.kwargs.get('perpage', 3)
        page = self.kwargs.get('page',1)

        paginator = Paginator(userCart, per_page=perpage)
        try:
            userCart = paginator.page(number=page)
        except EmptyPage:
            userCart = []

        uc_serialized = CartSerializer2(userCart, many=True)
        #if uc_serialized.is_valid(raise_exception=True):
        return Response(uc_serialized.data, 200)

    def post(self, request, *args, **kwargs):

        mydata = request.data.dict()
        mydata['user'] = request.user.id

        sanitized_data = CartSerializer(data=mydata)
        if sanitized_data.is_valid(raise_exception=True):
            sanitized_data.save()

            return_data = sanitized_data.data
            return_data.pop("user")

            return Response(return_data, status = 201)
      
    def delete(self, request, *args, **kwargs):
        
        Cart.objects.filter(user = request.user).delete()
        return Response(status=200)

class OrderManagementView(APIView):

    permission_classes = [IsAuthenticated,]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    
    def get(self, request, oid = None, *args, **kwargs):

        order_subset = None
        many = True

        by_date = request.query_params.get("date")
        by_crew = request.query_params.get("crew_id")
        price_gt = request.query_params.get("low_price")
        price_lt = request.query_params.get("high_price")

        perpage = request.query_params.get('perpage', 3)
        page = request.query_params.get('page',1)

        if request.user.groups.filter(name = "Manager").exists():
            order_subset = Order.objects.all()
            
            if by_date is not None:
                order_subset = order_subset.filter(date = by_date)
                
            if by_crew is not None:
                order_subset = order_subset.filter(delivery_crew__id = by_crew)
                
            if price_gt is not None:
                order_subset = order_subset.filter(total__gte = price_gt)
                
            if price_lt is not None:
                order_subset = order_subset.filter(total__lte = price_lt)

        elif request.user.groups.filter(name = "Delivery Crew").exists():
            order_subset = Order.objects.filter(delivery_crew = request.user)
        else:
            if oid is None:
                order_subset = Order.objects.filter(user = request.user)
            else:
                order_subset = Order.objects.get(id = oid)
                many = False
        
        co_deserialized = None

        if many:
            paginator = Paginator(order_subset, per_page=perpage)
            try:
                order_subset = paginator.page(number=page)
            except EmptyPage:
                order_subset = []

            co_deserialized = OrderSerializer2(order_subset, many=True)
        else:
            co_deserialized = OrderSerializer2(order_subset)
            
        return Response(co_deserialized.data, 200)

    def post(self, request, *args, **kwargs):

        currentCartItems = Cart.objects.filter(user = request.user)

        if currentCartItems is None:
            return Response(status=404)

        newOrder = Order.objects.create(user = request.user,
                                        delivery_crew = None,
                                        status = 0,
                                        total = 0,
                                        date = datetime.now().date())
        newOrder.save()
        total = 0

        for item in currentCartItems:
            oi_new = OrderItem.objects.create(
                order = newOrder,
                menuitem =  item.menuitem,
                quantity = item.quantity,
                unit_price = item.unit_price,
                price = item.price
            )

            total = total + item.price

            oi_new.save()
            item.delete()

        newOrder.total = total
        newOrder.save()
        return Response(status=201)
      
    def delete(self, request, oid = None, *args, **kwargs):
        
        if request.user.groups.filter(name = "Manager").exists():
            Order.objects.filter(id = oid).delete()
        else:
            raise PermissionError()

    def put(self, request, oid = None, *args, **kwargs):
        return self.updateOrder(request, oid, False)

    def patch(self, request, oid = None, *args, **kwargs):
        return self.updateOrder(request, oid, True)

    def updateOrder(self, request, oid, partial):

        order = Order.objects.get(id = oid)
        data_dict = request.data
        print(data_dict)

        if request.user.groups.filter(name = "Manager").exists():
            pass
        elif request.user.groups.filter(name = "Delivery Crew").exists():
            pass
        else:
            if order.user != request.user:
                raise PermissionError()

        serialized = OrderSerializer(instance=order, data=request.data, partial=partial)

        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return Response(serialized.data, 200)




