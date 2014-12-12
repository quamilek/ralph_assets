# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from ralph_assets.models_assets import Orientation
from ralph_assets.rest.asset_info_per_rack import (
    TYPE_EMPTY,
    TYPE_ACCESSORY,
    TYPE_ASSET,
)
from ralph_assets.tests.utils.assets import (
    AssetFactory,
    RackFactory,
    RackAccessoryFactory,
)


class TestRestAssetInfoPerRack(TestCase):
    def setUp(self):
        User.objects.create_superuser('test', 'test@test.test', 'test')
        self.client = APIClient()
        self.client.login(username='test', password='test')

        self.rack_1 = RackFactory(max_u_height=3)
        rack_2 = RackFactory()

        self.asset_1 = AssetFactory(device_info__position=1)
        self.asset_2 = AssetFactory(device_info__position=2)
        asset_3 = AssetFactory()

        self.rack_1.deviceinfo_set.add(self.asset_1.device_info)
        self.rack_1.deviceinfo_set.add(self.asset_2.device_info)
        rack_2.deviceinfo_set.add(asset_3.device_info)

        self.rack1_accessory = RackAccessoryFactory(
            rack=self.rack_1,
            server_room=self.rack_1.server_room,
            data_center=self.rack_1.server_room.data_center,
            orientation=Orientation.front,
        )
        self.rack2_accessory = RackAccessoryFactory(
            rack=rack_2,
            server_room=rack_2.server_room,
            data_center=rack_2.server_room.data_center,
            orientation=Orientation.front,
        )

    def tearDown(self):
        self.client.logout()

    def test_get(self):
        returned_json = json.loads(
            self.client.get(
                '/assets/api/rack/{0}/'.format(self.rack_1.id)
            ).content
        )
        expected_json = {
            'name': self.rack_1.name,
            'max_u_height': self.rack_1.max_u_height,
            'sides': [
                {
                    'type': 'front',
                    'items': [
                        {
                            '_type': TYPE_ASSET,
                            'asset_id': self.asset_1.id,
                            'url': self.asset_1.url,
                            'barcode': self.asset_1.barcode,
                            'sn': self.asset_1.sn,
                            'height': self.asset_1.model.height_of_device,
                            'position': self.asset_1.device_info.position,
                            'model': self.asset_1.model.name,
                        },
                        {
                            '_type': TYPE_ASSET,
                            'asset_id': self.asset_2.id,
                            'url': self.asset_2.url,
                            'barcode': self.asset_2.barcode,
                            'sn': self.asset_2.sn,
                            'height': self.asset_2.model.height_of_device,
                            'position': self.asset_2.device_info.position,
                            'model': self.asset_2.model.name,
                        }, {



                            '_type': TYPE_ACCESSORY,
                            'position': self.rack1_accessory.position,
                            'remarks': self.rack1_accessory.remarks,
                            'type': self.rack1_accessory.accessory.name,



                        }, {
                            '_type': TYPE_EMPTY,
                            'position': 3,
                        }
                    ]
                },
                {
                    'type': 'back',
                    'items': [
                        {
                            '_type': TYPE_EMPTY,
                            'position': 1,
                        },
                        {
                            '_type': TYPE_EMPTY,
                            'position': 2,
                        },
                        {
                            '_type': TYPE_EMPTY,
                            'position': 3,
                        }
                    ],
                }
            ]
        }
        self.assertEquals(returned_json, expected_json)
