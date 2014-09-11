# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from bob.views import DependencyView

from django.contrib.auth.models import User
from django.forms.models import formset_factory
from django.http import HttpResponseBadRequest, HttpResponse
from django.views.generic import TemplateView

from ralph_assets.forms_multi import XXXForm
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


class MultiFormRowAjaxView(TemplateView):
    template_name = 'assets/ajax_template/multi_form_row.html'

    def get(self, *args, **kwargs):
        replace_id = self.request.GET.get('replace_id')
        response = super(MultiFormRowAjaxView, self).get(
            replace_id=replace_id, *args, **kwargs
        )
        return HttpResponse(response.render().content.replace(
            '-0-', '-{}-'.format(replace_id)
        ))

    def get_context_data(self, replace_id, **kwargs):
        MultiAssignFormSet = formset_factory(form=XXXForm, extra=1)
        return {
            'formset': MultiAssignFormSet(initial={}),
            'replace_id': int(replace_id) + 1,
        }
