from .views import MenuItemsViewMultiple, MenuItemsViewSingle, ManagerGroupView, DeliveryCrewGroupView, CartManagementView, OrderManagementView, CategoryItemViewMultiple
from django.urls import path

urlpatterns = [
    path('categories/', CategoryItemViewMultiple.as_view(), name="category_view"),
    path('menu-items/', MenuItemsViewMultiple.as_view(), name="menu_items_multiple"),
    path('menu-items/<int:menuItem>', MenuItemsViewSingle.as_view(), name="menu_items_single"),
    path('groups/manager/users', ManagerGroupView.as_view(), name="manager_group"),
    path('groups/manager/users/<int:userId>', ManagerGroupView.as_view(), name="manager_group_single"),
    path('groups/delivery-crew/users', DeliveryCrewGroupView.as_view(), name="dc_group"),
    path('groups/delivery-crew/users/<int:userId>', DeliveryCrewGroupView.as_view(), name="dc_group_single"),
    path('cart/menu-items/', CartManagementView.as_view(), name="cart"),
    path('orders/', OrderManagementView.as_view(), name="order_management_list"),
    path('orders/<int:oid>', OrderManagementView.as_view(), name="order_management")
]