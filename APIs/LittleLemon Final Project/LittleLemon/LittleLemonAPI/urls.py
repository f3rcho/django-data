from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [

    # USERS
    path('api-token-auth/', obtain_auth_token),
    path('users', views.Users.as_view()),
    path('users/users/me/', views.me),
    # MENU ITEMS
    path('menu-items', views.MenuItemsList.as_view()),
    path('menu-items/<int:pk>', views.MenuItem.as_view()),
    # ORDERS
    path('orders', views.orderlist),
    path('orders/<int:pk>', views.orderDetail),
    # CARTs
    path('cart/menu-items', views.cartList),
    # USER GROUPS
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:pk>', views.deleteUserfromGroup),
    # DELIVERY-CREW GROUPS
    path('groups/delivery-crew/users', views.deliveryCrew),
    path('groups/delivery-crew/users/<int:pk>',
         views.deleteUserfromDeliveryGroup),

]
urlpatterns = format_suffix_patterns(urlpatterns)

# urlpatterns = [
#     path('categories', views.CategoriesView.as_view()),
#     path('menu-items', views.MenuItemsView.as_view()),
#     path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
#     path('cart/menu-items', views.CartView.as_view()),
#     path('orders', views.OrderView.as_view()),
#     path('orders/<int:pk>', views.SingleOrderView.as_view()),
#     path('groups/manager/users', views.GroupViewSet.as_view(
#         {'get': 'list', 'post': 'create', 'delete': 'destroy'})),

#     path('groups/delivery-crew/users', views.DeliveryCrewViewSet.as_view(
#         {'get': 'list', 'post': 'create', 'delete': 'destroy'}))
# ]
