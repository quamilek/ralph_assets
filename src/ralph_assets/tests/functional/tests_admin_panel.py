# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase

from ralph.ui.tests.global_utils import login_as_su
from ralph_assets.models_dc_assets import Rack
from ralph_assets.tests.utils.assets import DataCenterFactory, RackFactory


class TestRackForm(TestCase):

    def setUp(self):
        self.client = login_as_su()
        self.dc_1 = DataCenterFactory(
            visualization_cols_num=10, visualization_rows_num=10,
        )
        self.rack_1 = RackFactory(
            data_center=self.dc_1, visualization_col=1, visualization_row=1,
        )

    def test_collisions_validation(self):
        # add with collisions
        url = reverse('admin:ralph_assets_rack_add')
        response = self.client.post(
            url,
            {
                'name': 'Rack 123',
                'data_center': self.dc_1.id,
                'max_u_height': 48,
                'orientation': 1,
                'visualization_col': 1,
                'visualization_row': 1,
                'rackaccessory_set-TOTAL_FORMS': 0,
                'rackaccessory_set-INITIAL_FORMS': 0,
                'rackaccessory_set-MAX_NUM_FORMS': 0,
            },
            follow=True,
        )
        self.assertFalse(response.context_data['adminform'].form.is_valid())
        message = response.context_data['adminform'].form.non_field_errors()[0]
        self.assertEqual(
            'Selected possition collides with racks: {}.'.format(
                self.rack_1.name,
            ),
            message,
        )
        # update
        url = reverse(
            'admin:ralph_assets_rack_change', args=(self.rack_1.id,)
        )
        response = self.client.post(
            url,
            {
                'name': self.rack_1.name,
                'data_center': self.dc_1.id,
                'max_u_height': 48,
                'orientation': 1,
                'visualization_col': 1,
                'visualization_row': 1,
                'rackaccessory_set-TOTAL_FORMS': 0,
                'rackaccessory_set-INITIAL_FORMS': 0,
                'rackaccessory_set-MAX_NUM_FORMS': 0,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            reverse(
                'admin:ralph_assets_rack_changelist',
            ) in response.request['PATH_INFO'],
        )
        # add without collisions
        url = reverse('admin:ralph_assets_rack_add')
        response = self.client.post(
            url,
            {
                'name': 'Rack 123',
                'data_center': self.dc_1.id,
                'max_u_height': 48,
                'orientation': 1,
                'visualization_col': 5,
                'visualization_row': 5,
                'rackaccessory_set-TOTAL_FORMS': 0,
                'rackaccessory_set-INITIAL_FORMS': 0,
                'rackaccessory_set-MAX_NUM_FORMS': 0,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            reverse(
                'admin:ralph_assets_rack_changelist',
            ) in response.request['PATH_INFO'],
        )
        self.assertTrue(Rack.objects.filter(
            name='Rack 123', data_center=self.dc_1.id, max_u_height=48,
            visualization_col=5, visualization_row=5,
        ).exists())

    def test_dimensions_validation(self):
        url = reverse('admin:ralph_assets_rack_add')
        # To big visualization_col number.
        response = self.client.post(
            url,
            {
                'name': 'Rack 123',
                'data_center': self.dc_1.id,
                'max_u_height': 48,
                'visualization_col': 11,
                'visualization_row': 1,
                'rackaccessory_set-TOTAL_FORMS': 0,
                'rackaccessory_set-INITIAL_FORMS': 0,
                'rackaccessory_set-MAX_NUM_FORMS': 0,
            },
            follow=True,
        )
        self.assertFalse(response.context_data['adminform'].form.is_valid())
        message = response.context_data['adminform'].form.non_field_errors()[0]
        self.assertEqual(
            'Maximum allowed column number for selected data center is 10.',
            message,
        )
        # To big visualization_row number.
        response = self.client.post(
            url,
            {
                'name': 'Rack 123',
                'data_center': self.dc_1.id,
                'max_u_height': 48,
                'visualization_col': 1,
                'visualization_row': 11,
                'rackaccessory_set-TOTAL_FORMS': 0,
                'rackaccessory_set-INITIAL_FORMS': 0,
                'rackaccessory_set-MAX_NUM_FORMS': 0,
            },
            follow=True,
        )
        self.assertFalse(response.context_data['adminform'].form.is_valid())
        message = response.context_data['adminform'].form.non_field_errors()[0]
        self.assertEqual(
            'Maximum allowed row number for selected data center is 10.',
            message,
        )
