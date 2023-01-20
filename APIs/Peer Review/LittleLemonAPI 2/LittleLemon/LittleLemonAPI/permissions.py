from rest_framework import permissions

class ManagerWriteOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if request.user.groups.filter(name = "Manager").exists():
            return True
        elif request.method in permissions.SAFE_METHODS:
            return True
        else:
            return False

class ManagerOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        
        if request.user.groups.filter(name = "Manager").exists():
            return True
        else:
            return False