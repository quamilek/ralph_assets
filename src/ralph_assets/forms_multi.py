# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from ajax_select.fields import (
    AutoCompleteSelectField,
)
from ralph_assets.forms import LOOKUPS


class IntegerWidget(forms.TextInput):
    input_type = 'number'


class BaseForm(forms.Form):
    delete = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
    )
    licence_count = forms.IntegerField(
        min_value=1,
        widget=IntegerWidget(attrs={
            'type': 'number',
            'min': 1,
            'step': 1,
            'class': 'licence-count-input',
        }),
        initial=1,
    )

    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = self.order_fields


class AssetLicenceAssignForm(BaseForm):
    order_fields = ['delete', 'asset', 'licence_count']
    asset = AutoCompleteSelectField(
        LOOKUPS['linked_device'], required=False, label=_('Asset')
    )


class UserLicenceAssignForm(BaseForm):
    order_fields = ['delete', 'user', 'licence_count']
    user = AutoCompleteSelectField(
        LOOKUPS['asset_user'], required=False, label=_('User')
    )
