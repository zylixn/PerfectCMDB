from cmdb import models
from rest_framework import viewsets,authentication,permissions,exceptions,filters
from .serializers import AssetSerializer

class DefaultsMixin(object):
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    paginate_by = 5
    paginate_by_param = 'page_size'
    max_paginate_by = 5
    filter_backends = (
        #filters.DjangoObjectPermissionsFilter,
        filters.SearchFilter,
        filters.OrderingFilter,
    )



class AssetViewSet(DefaultsMixin,viewsets.ModelViewSet):
    queryset = models.Asset.objects.all()
    serializer_class = AssetSerializer
    search_fields = ('name','sn','management_ip')
    ordering_fields = ('sn','trade_date')

