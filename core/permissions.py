from rest_framework.permissions import BasePermission
from apps.api.models import Account

# Validate Admin permission
class Admin(BasePermission):
    def has_permission(self, request, view):
        return check_user_permission(request.user, ["A"])

# Validate staff permission
class Staff(BasePermission):
    def has_permission(self, request, view):
        return check_user_permission(request.user, ["A","B"])

# Validate branded permission
class Branded(BasePermission):
    def has_permission(self, request, view):
        return check_user_permission(request.user, ["A","B","C"])

# Validate authenticated permission
class Authenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

# Validate visitors permission
class Visitors(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated

# Check user permission
def check_user_permission(user, permissions):
    if user and user.is_authenticated:
        account = Account.objects.get(user=user)
        if account.type in permissions:
            return True
        else:
            return False
    else:
        return False
