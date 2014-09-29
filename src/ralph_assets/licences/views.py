# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools as it
import urllib

from bob.data_table import DataTableColumn

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Sum, Count
from django.forms.models import formset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from ralph_assets.forms_multi import (
    AssetLicenceAssignForm,
)
from ralph_assets.licences.forms import (
    SoftwareCategorySearchForm,
    LicenceSearchForm,
    AddLicenceForm,
    EditLicenceForm,
    BulkEditLicenceForm,
)
from ralph_assets.views.base import SubmoduleModeMixin
from ralph_assets.models_assets import MODE2ASSET_TYPE
from ralph_assets.licences.models import (
    Licence,
    LicenceAsset,
    SoftwareCategory,
)
from ralph_assets.utils import assigned_formset_factory
from ralph_assets.views.base import (
    AssetsBase,
    AjaxMixin,
    BulkEditBase,
    JsonResponseMixin,
)
from ralph_assets.views.search import GenericSearch


LICENCE_PAGE_SIZE = 10


class LicenseSelectedMixin(object):
    submodule_name = 'licences'


class LicenceBaseView(LicenseSelectedMixin, AssetsBase):
    pass


class SoftwareCategoryNameColumn(DataTableColumn):
    """A column with software category name linking to the search of
    licences"""

    def render_cell_content(self, resource):
        name = super(
            SoftwareCategoryNameColumn, self
        ).render_cell_content(resource)
        return '<a href="{link}?{qs}">{name}</a>'.format(
            link=reverse('licences_list'),
            qs=urllib.urlencode({'software_category': resource.id}),
            name=name,
        )


class LicenceLinkColumn(DataTableColumn):
    """A column that links to the edit page of a licence simply displaying
    'Licence' in a grid"""
    def render_cell_content(self, resource):
        return '<a href="{url}">{licence}</a>'.format(
            url=resource.url,
            licence=unicode(_('Licence')),
        )


class SoftwareCategoryList(LicenseSelectedMixin, GenericSearch):
    """Displays a list of software categories, which link to searches for
    licences."""

    Model = SoftwareCategory
    Form = SoftwareCategorySearchForm
    columns = [
        SoftwareCategoryNameColumn(
            'Name',
            bob_tag=True,
            field='name',
            sort_expression='name',
        ),
    ]


class CheckBoxColumn(DataTableColumn):
    """A column to select items in a grid"""
    def render_cell_content(self, resource):
        return '<input type="checkbox" name="select" value="{}">'.format(
            resource.id,
        )


class LicenceList(LicenseSelectedMixin, GenericSearch):
    """Displays a list of licences."""

    active_sidebar_item = 'search'
    template_name = 'assets/licence_list.html'

    Model = Licence
    Form = LicenceSearchForm
    columns = [
        CheckBoxColumn(
            _('Dropdown'),
            selectable=True,
            bob_tag=True,
        ),
        LicenceLinkColumn(
            _('Type'),
            bob_tag=True,
        ),
        DataTableColumn(
            _('Inventory number'),
            bob_tag=True,
            field='niw',
            sort_expression='niw',
        ),
        DataTableColumn(
            _('Licence Type'),
            bob_tag=True,
            field='licence_type__name',
            sort_expression='licence_type__name',
        ),
        DataTableColumn(
            _('Manufacturer'),
            bob_tag=True,
            field='manufacturer__name',
            sort_expression='manufacturer__name',
        ),
        DataTableColumn(
            _('Software Category'),
            bob_tag=True,
            field='software_category',
            sort_expression='software_category__name',
        ),
        DataTableColumn(
            _('Property of'),
            bob_tag=True,
            field='property_of__name',
            sort_expression='property_of__name',
        ),
        DataTableColumn(
            _('Number of purchased items'),
            bob_tag=True,
            field='number_bought',
            sort_expression='number_bought',
        ),
        DataTableColumn(
            _('Used'),
            bob_tag=True,
            field='used',
        ),
        DataTableColumn(
            _('Invoice date'),
            bob_tag=True,
            field='invoice_date',
            sort_expression='invoice_date',
        ),
        DataTableColumn(
            _('Invoice no.'),
            bob_tag=True,
            field='invoice_no',
            sort_expression='invoice_no',
        ),
        DataTableColumn(
            _('Valid thru'),
            bob_tag=True,
            field='valid_thru',
            sort_expression='valid_thru',
        ),
        DataTableColumn(
            _('Created'),
            bob_tag=True,
            field='created',
            sort_expression='created',
        ),
    ]

    def get_context_data(self, **kwargs):
        context = super(LicenceList, self).get_context_data(**kwargs)
        context.update({'get_query': self.request.GET.urlencode()})
        return context


class LicenceFormView(LicenceBaseView):
    """Base view that displays licence form."""
    template_name = 'assets/add_licence.html'

    def _get_form(self, data=None, **kwargs):
        self.form = self.Form(
            mode=self.mode, data=data, **kwargs
        )

    def get_context_data(self, **kwargs):
        ret = super(LicenceFormView, self).get_context_data(**kwargs)
        ret.update({
            'form': self.form,
            'form_id': 'add_licence_form',
            'edit_mode': False,
            'caption': self.caption,
            'licence': getattr(self, 'licence', None),
            'mode': 'back_office',  # -1 to technical debt
        })
        return ret

    def _save(self, request, *args, **kwargs):
        try:
            licence = self.form.save(commit=False)
            if licence.asset_type is None:
                licence.asset_type = MODE2ASSET_TYPE[self.mode]
            licence.save()
            # TODO: manually save attachments, users, assets
            # save_m2m() doesn't support models where in many-to-many field
            # is specified `through` attr
            # self.form.save_m2m()
            messages.success(self.request, self.message)
            return HttpResponseRedirect(licence.url)
        except ValueError:
            return super(LicenceFormView, self).get(request, *args, **kwargs)


class AddLicence(LicenceFormView):
    """Add a new licence"""
    active_sidebar_item = 'add licence'
    caption = _('Add Licence')
    message = _('Licence added')
    Form = AddLicenceForm

    def get(self, request, *args, **kwargs):
        self._get_form()
        return super(AddLicence, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self._get_form(request.POST)
        if self.form.is_valid():
            sns = self.form.cleaned_data['sn'] or it.repeat(None)
            for sn, niw in zip(sns, self.form.cleaned_data['niw']):
                self.form.instance.pk = None
                licence = self.form.save(commit=False)
                if licence.asset_type is None:
                    licence.asset_type = MODE2ASSET_TYPE[self.mode]
                licence.sn = sn
                licence.niw = niw
                licence.save()
            messages.success(self.request, '{} licences added'.format(len(
                self.form.cleaned_data['niw'],
            )))
            return HttpResponseRedirect(reverse('licences_list'))
        else:
            return super(AddLicence, self).get(request, *args, **kwargs)


class EditLicence(LicenceFormView):
    """Edit licence"""
    detect_changes = True
    caption = _('Edit Licence')
    message = _('Licence changed')
    Form = EditLicenceForm

    def get(self, request, licence_id, *args, **kwargs):
        self.licence = Licence.objects.get(pk=licence_id)
        self._get_form(instance=self.licence)
        return super(EditLicence, self).get(request, *args, **kwargs)

    def post(self, request, licence_id, *args, **kwargs):
        self.licence = Licence.objects.get(pk=licence_id)
        self._get_form(request.POST, instance=self.licence)
        return self._save(request, *args, **kwargs)


class LicenceBulkEdit(BulkEditBase, LicenceBaseView):
    model = Licence
    template_name = 'assets/bulk_edit.html'
    form_bulk = BulkEditLicenceForm


class CountLicence(AjaxMixin, JsonResponseMixin, GenericSearch):
    mainmenu_selected = 'licences'  # required by AssetBase
    Model = Licence
    Form = LicenceSearchForm

    def get(self, request, *args, **kwargs):
        self.form = self.Form(request.GET)
        qs = self.handle_search_data(request)
        summary = qs.aggregate(total=Sum('number_bought'))
        summary.update(qs.annotate(assets_count=Count('assets')).aggregate(
            used_by_assets=Sum('assets_count'),
        ))
        summary.update(qs.annotate(users_count=Count('users')).aggregate(
            used_by_users=Sum('users_count'),
        ))
        return self.render_json_response(summary)


class LicenceConnectionsView(SubmoduleModeMixin, AssetsBase):
    template_name = 'assets/licence_connections.html'
    submodule_name = 'licences'

    def get(self, *args, **kwargs):
        self.licence = Licence.objects.get(id=kwargs.get('licence_id'))
        self.licence = get_object_or_404(
            Licence.objects, id=kwargs.get('licence_id'),
        )
        return super(LicenceConnectionsView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return super(LicenceConnectionsView, self).get(*args, **kwargs)

    def prepare_formset(self, *args, **kwargs):
        empty_formset = formset_factory(
            form=AssetLicenceAssignForm, extra=1,
        )(initial={})

        AssetFormsetFactory = formset_factory(
            form=AssetLicenceAssignForm, extra=2,
        )
        # assets = self.licence.assets.all()
        asset_connections_formset = AssetFormsetFactory(
            initial={}, prefix='assets',
        )
        # UserFormsetFactory = formset_factory(
        #     form=UserLicenceAssignForm, extra=2,
        # )
        # user_connections_formset = UserFormsetFactory(
        #     initial={}, prefix='users',
        # )
        return {
            'empty_formset': empty_formset,
            'asset_connections_formset': asset_connections_formset(),
            # 'user_connections_formset': user_connections_formset,
        }

    def get_context_data(self, *args, **kwargs):
        context = super(LicenceConnectionsView, self).get_context_data(
            *args, **kwargs
        )
        context.update(self.prepare_formset())
        context.update({
            'licence': self.licence,
            'caption': _('Edit Licence relations')
        })
        return context


class AssginLicenceMixin(object):
    template_name = 'assets/generic/assign_licence.html'
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

    def formset_save(self, obj):
        raise NotImplementedError('Please override formset_valid method.')

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object(*args, **kwargs)
        query_kwargs = {obj.__class__.__name__.lower(): obj}
        queryset = self.get_base_model().objects.filter(**query_kwargs)
        self.empty_formset = assigned_formset_factory(
            obj=obj,
            base_model=self.get_base_model(),
            field=self.get_base_field(),
            lookup=self.lookup,
        )(queryset=self.get_base_model().objects.none())

        self.formset = assigned_formset_factory(
            obj=obj,
            base_model=self.get_base_model(),
            field=self.get_base_field(),
            lookup=self.lookup,
            extra=1
        )(request.POST or None, queryset=queryset)
        return super(AssginLicenceMixin, self).dispatch(
            request, *args, **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super(AssginLicenceMixin, self).get_context_data(**kwargs)
        context.update({
            'formset': self.formset,
            'empty_formset': self.empty_formset,
        })
        return context

    def post(self, request, *args, **kwargs):
        if self.formset.is_valid():
            self.formset.save()
            # self.formset_save(self.get_object(*args, **kwargs))
        return self.get(request, *args, **kwargs)


from ralph_assets.forms import LOOKUPS


class AssginAsset2Licence(AssginLicenceMixin, AssetsBase):
    submodule_name = 'hardware'
    base_model = LicenceAsset
    base_field = 'asset'
    lookup = LOOKUPS['linked_device']

    def get_object(self, licence_id, *args, **kwargs):
        return Licence.objects.get(id=licence_id)

    def formset_save(self, obj):
        for data in self.formset.cleaned_data:
            obj.assign(
                data[self.base_field],
                data['quantity'],
            )
