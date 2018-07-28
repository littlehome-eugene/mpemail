from rest_framework import permissions

from site_common.rest.permissions.owner_permission import OwnerPermission


class ImagePermission(OwnerPermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_authenticated() and request.user.is_staff:
            return True

        owner_user = self.get_owner_user(obj)
        if request.method in ['DELETE']:
            if owner_user is None:
                return False
            if self.is_same_user(owner_user, request.user):
                return True
            return False

        if request.method in ['POST']:
            if request.user.is_authenticated():
                return True

        if request.method in ['PUT', 'PATCH']:
            return self.is_same_user(owner_user, request.user)

        return True
