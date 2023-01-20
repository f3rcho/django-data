from rest_framework import permissions, status
from rest_framework.response import Response


class IsCustomerOrDeliveryCrew(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.groups.filter(name='Manager').exists():
            return True
