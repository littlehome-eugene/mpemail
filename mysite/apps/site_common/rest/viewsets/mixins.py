from django.http import Http404

from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response


class MultiSerializerViewSetMixin(object):
    """
    client of this mixin class needs to define
    serializer_dict = {
    }
    # http://stackoverflow.com/a/22922156/433570
    """

    def get_serializer_class(self):

        try:
            return self.serializer_dict[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()


class MultiPaginationViewSetMixin(object):
    """
    client of this mixin class needs to define
    pagination_class_dict = {
    }
    """

    @property
    def paginator(self):

        if not hasattr(self, '_paginator'):
            try:
                pagination_class = self.pagination_class_dict[self.action]
                self._paginator = pagination_class()

            except (KeyError, AttributeError):
                return super(MultiPaginationViewSetMixin, self).paginator

        return self._paginator


class ShareMixin(object):

    @detail_route(methods=['post', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def share(self, request, object_id, **kwargs):

        model = self.queryset.model
        lookup_kwargs = {}
        if object_id:
            lookup_kwargs['%s__exact' % model._meta.pk.name] = object_id

        try:
            obj = model._default_manager.get(**lookup_kwargs)
        except model.DoesNotExist:
            raise Http404('No %s found for %s.' %
                          (model._meta.app_label, lookup_kwargs))

        obj.increment_share_count()

        return Response({'share_count': obj.share_count})
