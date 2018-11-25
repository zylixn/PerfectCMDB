from cmdb import models
from rest_framework import serializers
from rest_framework.reverse import reverse

class AssetSerializer(serializers.ModelSerializer):
    contract = serializers.SlugRelatedField(slug_field='name',required=False,
                                            allow_null=True,queryset=models.Contract.objects.all())
    asset_type_display = serializers.SerializerMethodField()
    manufactory_display = serializers.SerializerMethodField()
    links = serializers.SerializerMethodField()

    class Meta:
        model = models.Asset
        fields = ('asset_type','asset_type_display','name','sn','manufactory','manufactory_display','management_ip',
                    'contract','links')

    def get_asset_type_display(self, obj):
        return obj.get_asset_type_display()

    def get_manufactory_display(self,obj):
        return obj.get_asset_type_display()

    def get_links(self,obj):
        request = self.context['request']
        return {
            'self':reverse('asset-detail',
                           kwargs={'pk':obj.pk},request=request)
            }
