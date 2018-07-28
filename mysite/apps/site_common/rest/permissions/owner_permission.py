from rest_framework import permissions


class OwnerPermission(permissions.BasePermission):

    def is_same_user(self, owner_user, request_user):
        if not request_user.is_authenticated():
            return False

        if owner_user == request_user:
            return True
        return False

    def get_owner_user(self, obj):
        return obj.user

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            owner_user = self.get_owner_user(obj)
            return self.is_same_user(owner_user, request.user)

        # else create
        return True


class OwnerStaffPermission(OwnerPermission):
    """
    owner or staff can do anything other than delete
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated() and request.user.is_staff:
            return True

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            owner_user = self.get_owner_user(obj)
            return self.is_same_user(owner_user, request.user)

        return True
