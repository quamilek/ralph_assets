# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.http import Http404

from rest_framework.response import Response
from rest_framework.views import APIView

from ralph_assets.models_assets import Orientation, Rack
from ralph_assets.models_dc_assets import RackAccessory
from ralph_assets.views.base import ACLGateway


TYPE_EMPTY = 'empty'
TYPE_ACCESSORY = 'accessory'
TYPE_ASSET = 'asset'


from ralph_assets.rest.serializers.models_dc_asssets import (
    AssetSerializer,
    RackAccessorySerializer,
    RackSerializer,
)


class AssetsView(ACLGateway, APIView):

    def get_object(self, pk):
        try:
            return Rack.objects.get(id=pk)
        except Rack.DoesNotExist:
            raise Http404

    def _get_assets(self, rack, side):
        return AssetSerializer(rack.get_root_assets(side), many=True).data

    def _get_accessories(self, rack, side):
        accessories = RackAccessory.objects.select_related('accessory').filter(
            rack=rack,
            orientation=side,
        )
        return RackAccessorySerializer(accessories, many=True).data

    def get(self, request, rack_id, format=None):
        rack = self.get_object(rack_id)
        devices = {}
        for side in [Orientation.front, Orientation.back]:
            devices[side.desc] = (
                self._get_assets(rack, side) +
                self._get_accessories(rack, side)
            )
        devices['info'] = RackSerializer(rack).data
        return Response(devices)
