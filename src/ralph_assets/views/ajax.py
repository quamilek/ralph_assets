# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bob.views import DependencyView

from django.contrib.auth.models import User
from django.http import HttpResponseBadRequest

from ralph_assets.models_assets import AssetModel
from ralph_assets.views.base import ACLGateway


class CategoryDependencyView(DependencyView, ACLGateway):
    def get_values(self, value):
        try:
            profile = User.objects.get(pk=value).profile
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return HttpResponseBadRequest("Incorrect user id")
        values = dict(
            [(name, getattr(profile, name)) for name in (
                'location',
                'company',
                'employee_id',
                'cost_center',
                'profit_center',
                'department',
                'manager',
            )]
        )
        return values


class ModelDependencyView(DependencyView, ACLGateway):
    def get_values(self, value):
        category = ''
        if value != '':
            try:
                category = AssetModel.objects.get(pk=value).category_id
            except (
                AssetModel.DoesNotExist,
                AssetModel.MultipleObjectsReturned,
            ):
                return HttpResponseBadRequest("Incorrect AssetModel pk")
        return {
            'category': category,
        }
