# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.translation import ugettext as _

from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from ralph_assets.models_assets import DataCenter
from ralph_assets.views.base import ACLGateway


class DCRacksAPIView(ACLGateway, APIView):
    """
    Return information of list rack in data center with their positions.
    """
    def get(self, request, data_center_id, format=None):
        """
        Collecting racks information for given data_center id.

        :param data_center_id int: data_center id
        :returns list: list of informations about racks in given data center
        """
        try:
            data_center = DataCenter.objects.get(id=data_center_id)
        except DataCenter.DoesNotExist:
            return Response({
                'message': _('DataCenter with id `{0}` does not exist'.format(
                    data_center_id
                )),
            }, status=HTTP_404_NOT_FOUND)

        racks_data = data_center.rack_set.values(
            'id', 'name', 'visualization_col', 'visualization_row',
        )
        return Response(racks_data)
