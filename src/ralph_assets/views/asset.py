# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

from ralph_assets.models import Asset
from ralph_assets.licences.models import LicenceAsset
from ralph_assets.models_assets import AssetType
from ralph_assets.views.base import (
    ActiveSubmoduleByAssetMixin,
    AssetsBase,
    BulkEditBase,
    get_return_link,
)
from ralph_assets.views.search import _AssetSearch, AssetSearchDataTable
from ralph_assets.views.utils import _move_data, _update_office_info
from ralph.util.reports import Report


logger = logging.getLogger(__name__)


class DeleteAsset(AssetsBase):

    def post(self, *args, **kwargs):
        record_id = self.request.POST.get('record_id')
        try:
            self.asset = Asset.objects.get(
                pk=record_id
            )
        except Asset.DoesNotExist:
            messages.error(
                self.request, _("Selected asset doesn't exists.")
            )
            return HttpResponseRedirect(get_return_link(self.mode))
        else:
            if self.asset.type < AssetType.BO:
                self.back_to = '/assets/dc/'
            else:
                self.back_to = '/assets/back_office/'
            if self.asset.has_parts():
                parts = self.asset.get_parts_info()
                messages.error(
                    self.request,
                    _("Cannot remove asset with parts assigned. Please remove "
                        "or unassign them from device first. ".format(
                            self.asset,
                            ", ".join([str(part.asset) for part in parts])
                        ))
                )
                return HttpResponseRedirect(
                    '{}{}{}'.format(
                        self.back_to, 'edit/device/', self.asset.id,
                    )
                )
            # changed from softdelete to real-delete, because of
            # key-constraints issues (sn/barcode) - to be resolved.
            self.asset.delete_with_info()
            return HttpResponseRedirect(self.back_to)


class AssetSearch(Report, AssetSearchDataTable):
    """The main-screen search form for all type of assets."""
    active_sidebar_item = 'search'

    @property
    def submodule_name(self):
        return 'hardware_{mode}'.format(mode=self.mode)

    def get_context_data(self, *args, **kwargs):
        ret = super(AssetSearch, self).get_context_data(*args, **kwargs)
        ret.update({
            'url_query': self.request.GET,
            'active_submodule': 'hardware',  # TODO: stored in session
        })
        return ret


class AssetBulkEdit(ActiveSubmoduleByAssetMixin, BulkEditBase, _AssetSearch):
    model = Asset
    commit_on_valid = False

    def get_object_class(self):
        return self.model

    def initial_forms(self, formset, queryset):
        for idx, asset in enumerate(queryset):
            if asset.office_info:
                for field in ['purpose']:
                    if field not in formset.forms[idx].fields:
                        continue
                    formset.forms[idx].fields[field].initial = (
                        getattr(asset.office_info, field, None)
                    )

    def save_formset(self, instances, formset):
        with transaction.commit_on_success():
            for idx, instance in enumerate(instances):
                instance.modified_by = self.request.user.get_profile()
                instance.save(user=self.request.user)
                new_src, office_info_data = _move_data(
                    formset.forms[idx].cleaned_data,
                    {}, ['purpose']
                )
                formset.forms[idx].cleaned_data = new_src
                instance = _update_office_info(
                    self.request.user, instance,
                    office_info_data,
                )

    def handle_formset_error(self, formset_error):
        messages.error(
            self.request,
            _(('Please correct errors and check both "serial numbers" and '
               '"barcodes" for duplicates'))
        )


from django import forms
from ajax_select.fields import (
    AutoCompleteSelectField,
)
from ralph_assets.forms import LOOKUPS

from django.forms.models import modelformset_factory


def assgined_formset_factory(obj, base_model, field, lookup,
                             extra_exclude=None):
    obj_class_name = obj.__class__.__name__.lower()
    if obj_class_name == field:
        raise Exception('Nie można podawać takich samych pól')
    if obj.__class__ == base_model:
        raise Exception('Nie można podawać takich samych modeli')

    class Form(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(Form, self).__init__(*args, **kwargs)
            self.fields[field] = AutoCompleteSelectField(lookup, required=True)

        class Meta:
            model = base_model
            exclude = [obj_class_name] + (extra_exclude or [])

    formset = modelformset_factory(
        model=base_model,
        form=Form,
    )
    return formset


class AssginLicenceMixin(object):
    template_name = 'assets/generic/assign_licence.html'
    extra = 1
    base_model = None

    def get_object(self, *args, **kwargs):
        raise NotImplementedError

    def get_base_model(self):
        if not self.base_model:
            raise NotImplementedError('Please specified base_model or override'
                                      ' get_base_model method.')
        return self.base_model

    def get_base_field(self):
        if not self.base_field:
            raise NotImplementedError('Please specified base_field or override'
                                      ' get_base_field method.')
        return self.base_field

    def formset_valid(self, obj):
        raise NotImplementedError('Please override formset_valid method.')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        queryset = self.get_base_model().objects.filter(asset=obj)
        self.formset = assgined_formset_factory(
            obj=obj,
            base_model=self.get_base_model(),
            field=self.get_base_field(),
            lookup=self.lookup,
        )(request.POST or None, queryset=queryset)
        return super(AssginLicenceMixin, self).dispatch(
            request, *args, **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(AssginLicenceMixin, self).get_context_data(**kwargs)
        context['formset'] = self.formset
        return context

    def post(self, request, *args, **kwargs):
        if self.formset.is_valid():
            self.formset_valid(self.get_object(*args, **kwargs))
        return self.get(request, *args, **kwargs)


class AssginLicence(AssginLicenceMixin, AssetsBase):
    submodule_name = 'hardware'
    base_model = LicenceAsset
    base_field = 'licence'
    lookup = LOOKUPS['free_licences']

    def get_object(self, asset_id, *args, **kwargs):
        return Asset.objects.get(id=asset_id)

    def formset_valid(self, obj):
        for data in self.formset.cleaned_data:
            data['licence'].assign(
                obj,
                data['quantity'],
            )
