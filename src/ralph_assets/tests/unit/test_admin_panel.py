# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.forms import ValidationError
from django.test import TestCase

from ralph_assets.admin import _greater_than_zero_validation


class TestAdditionalValidators(TestCase):

    def test_greater_than_zero_validation(self):
        self.assertRaises(
            ValidationError, _greater_than_zero_validation, 0)
        self.assertRaises(
            ValidationError, _greater_than_zero_validation, -1)
        self.assertIsNone(_greater_than_zero_validation(1))
