# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from bob.menu import MenuItem, MenuHeader
from bob.data_table import DataTableColumn
from bob.views.bulk_edit import BulkEditBase as BobBulkEditBase

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from ralph.account.models import Perm
from ralph_assets import VERSION
from ralph_assets import forms as assets_forms
from ralph_assets.models_assets import AssetType
from ralph_assets.models import Asset
from ralph_assets.forms import OfficeForm

logger = logging.getLogger(__name__)


def get_return_link(mode):
    return "/assets/%s/" % mode


class ACLGateway(object):
    """
    Assets module class which mainly checks user access to page.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.get_profile().has_perm(Perm.has_assets_access):
            raise PermissionDenied
        return super(ACLGateway, self).dispatch(request, *args, **kwargs)


class Base(TemplateView):
    columns = []
    status = ''
    section = None

    def get_mainmenu_items(self):
        mainmenu = [
            MenuItem(
                fugue_icon='fugue-building',
                href=reverse('asset_search', kwargs={'mode': 'dc'}),
                label=_('Data center'),
                name='dc',
            ),
            MenuItem(
                fugue_icon='fugue-printer',
                href=reverse('asset_search', kwargs={'mode': 'back_office'}),
                label=_('BackOffice'),
                name='back_office',
            ),
            MenuItem(
                fugue_icon='fugue-lifebuoy',
                href=reverse('support_list'),
                label=_('Supports'),
                name='supports',
            ),
            MenuItem(
                fugue_icon='fugue-user-green-female',
                href=reverse('user_list'),
                label=_('User list'),
                name='user list',
            ),
            MenuItem(
                fugue_icon='fugue-cheque',
                href=reverse('licence_list'),
                label=_('Licences'),
                name='licences',
            ),
            MenuItem(
                fugue_icon='fugue-table',
                href=reverse('reports'),
                label=_('Reports'),
                name='reports',
            ),
        ]
        return mainmenu

    def get_footer_items(self, details):
        footer_items = []
        if settings.BUGTRACKER_URL:
            footer_items.append(
                MenuItem(
                    fugue_icon='fugue-bug',
                    href=settings.BUGTRACKER_URL,
                    label=_('Report a bug'),
                    pull_right=True,
                )
            )
        footer_items.append(
            MenuItem(
                fugue_icon='fugue-document-number',
                href=settings.CHANGELOG_URL,
                label=_(
                    "Version {version}".format(
                        version='.'.join((str(part) for part in VERSION)),
                    ),
                ),
            )
        )
        if self.request.user.is_staff:
            footer_items.append(
                MenuItem(
                    fugue_icon='fugue-toolbox',
                    href='/admin',
                    label=_('Admin'),
                )
            )
        footer_items.append(
            MenuItem(
                fugue_icon='fugue-user',
                href=reverse('user_preference', args=[]),
                label=_('{user} (preference)'.format(user=self.request.user)),
                pull_right=True,
                view_args=[details or 'info', ''],
                view_name='preference',
            )
        )
        footer_items.append(
            MenuItem(
                fugue_icon='fugue-door-open-out',
                href=settings.LOGOUT_URL,
                label=_('logout'),
                pull_right=True,
                view_args=[details or 'info', ''],
                view_name='logout',
            )
        )
        return footer_items

    def get_context_data(self, **kwargs):
        conetext = super(Base, self).get_context_data(**kwargs)
        details = self.kwargs.get('details', 'info')
        profile = self.request.user.get_profile()
        conetext.update({
            'columns': self.columns,
            'details': details,
            'footer_items': self.get_footer_items(details),
            'mainmenu_items': self.get_mainmenu_items(),
            'search_url': reverse('search', args=[details, '']),
            'show_bulk': profile.has_perm(Perm.bulk_edit),
            'url_query': self.request.GET,
            'user': self.request.user,
        })
        return conetext


class AssetsBase(ACLGateway, Base):
    template_name = "assets/base.html"
    sidebar_selected = None
    mainmenu_selected = None

    def get_context_data(self, *args, **kwargs):
        ret = super(AssetsBase, self).get_context_data(**kwargs)
        base_sidebar_caption = ''
        self.mainmenu_selected = self.mainmenu_selected or self.mode
        if self.mode == 'back_office':
            base_sidebar_caption = _('Back office actions')
        elif self.mode == 'dc':
            base_sidebar_caption = _('Data center actions')
        ret.update({
            'mainmenu_items': self.get_mainmenu_items(),
            'section': self.mainmenu_selected,
            'sidebar_items': self.get_sidebar_items(base_sidebar_caption),
            'sidebar_selected': self.sidebar_selected,
            'mode': self.mode,
            'multivalues_fields': ['sn', 'barcode', 'imei'],
            'asset_reports_enable': settings.ASSETS_REPORTS['ENABLE'],
        })
        return ret

    def get_sidebar_items(self, base_sidebar_caption):
        if self.mode in ('back_office', 'dc'):
            base_items = (
                ('add_device', _('Add device'), 'fugue-block--plus', True),
                ('add_part', _('Add part'), 'fugue-block--plus', True),
                ('asset_search', _('Search'), 'fugue-magnifier', True),
            )
        elif self.mainmenu_selected.startswith('licences'):
            base_items = (
                ('add_licence', _('Add licence'), 'fugue-cheque--plus', False),
            )
        elif self.mainmenu_selected.startswith('supports'):
            base_items = (
                ('add_support', _('Add Support'), 'fugue-block--plus', False),
            )
        else:
            base_items = ()
        other_items = (
            ('xls_upload', _('XLS upload'), 'fugue-cheque--plus', False),
        )
        items = [
            {'caption': base_sidebar_caption, 'items': base_items},
            {'caption': _('Others'), 'items': other_items},
        ]
        sidebar_menu = tuple()
        for item in items:
            menu_item = (
                [MenuHeader(item['caption'])] +
                [MenuItem(
                    label=label,
                    fugue_icon=icon,
                    href=(
                        reverse(view, kwargs={'mode': self.mode})
                        if modal else
                        reverse(view)
                    )
                ) for view, label, icon, modal in item['items']]
            )
            if sidebar_menu:
                sidebar_menu += menu_item
            else:
                sidebar_menu = menu_item
        sidebar_menu += [
            MenuItem(
                label='Admin',
                fugue_icon='fugue-toolbox',
                href=reverse('admin:app_list', args=('ralph_assets',))
            )
        ]
        return sidebar_menu

    def set_asset_objects(self, mode):
        if mode == 'dc':
            self.asset_objects = Asset.objects_dc
        elif mode == 'back_office':
            self.asset_objects = Asset.objects_bo

    def set_mode(self, mode):
        self.mode = mode

    def dispatch(self, request, mode=None, *args, **kwargs):
        self.request = request
        self.set_mode(mode)
        self.set_asset_objects(mode)
        return super(AssetsBase, self).dispatch(request, *args, **kwargs)

    def write_office_info2asset_form(self):
        """
        Writes fields from office_info form to asset form.
        """
        if self.asset.type in AssetType.BO.choices:
            self.office_info_form = OfficeForm(instance=self.asset.office_info)
            fields = ['imei', 'purpose']
            for field in fields:
                if field not in self.asset_form.fields:
                    continue
                self.asset_form.fields[field].initial = (
                    getattr(self.asset.office_info, field, '')
                )

    def form_dispatcher(self, class_name):
        """
        Returns form class depending on view mode ('backoffice' or
        'datacenter') and passed *class_name* arg.

        :param class_name: base class name common for both views BO, DC
        :returns class: form class from *ralph_assets.forms* module
        :rtype class:
        """
        mode_name = (
            'BackOffice' if self.mode == 'back_office' else 'DataCenter'
        )
        form_class_name = "{}{}Form".format(mode_name, class_name)
        try:
            form_class = getattr(assets_forms, form_class_name)
        except AttributeError:
            raise Exception("No form class named: {}".format(form_class_name))
        return form_class


class DataTableColumnAssets(DataTableColumn):
    """
    A container object for all the information about a columns header

    :param foreign_field_name - set if field comes from foreign key
    """

    def __init__(self, header_name, foreign_field_name=None, **kwargs):
        super(DataTableColumnAssets, self).__init__(header_name, **kwargs)
        self.foreign_field_name = foreign_field_name


class BulkEditBase(BobBulkEditBase):
    template_name = 'assets/bulk_edit.html'

    def get_form_bulk(self):
        if not self.form_bulk:
            return self.form_dispatcher('BulkEditAsset')
        else:
            return self.form_bulk

    def get_query_from_request(self, *args, **kwargs):
        if self.request.GET.get('from_query'):
            query = super(
                BulkEditBase, self,
            ).handle_search_data(self.args, self.kwargs)
        else:
            query = Q(pk__in=self.get_items_ids())
        return query
