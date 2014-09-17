# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from ralph_assets.licences.views import (
    AddLicence,
    CountLicence,
    EditLicence,
    LicenceList,
    LicenceBulkEdit,
    SoftwareCategoryList,
)
from ralph_assets.views.invoice_report import LicenceInvoiceReport


urlpatterns = patterns(
    '',
    url(
        r'^$',
        LicenceList.as_view(),
        name='licences_list',
    ),
    url(
        r'^invoice_report/$',
        LicenceInvoiceReport.as_view(),
        name='licences_invoice_report',
    ),
    url(
        r'^categories/$',
        SoftwareCategoryList.as_view(),
        name='software_categories',
    ),
    url(
        r'^bulkedit/',
        LicenceBulkEdit.as_view(),
        name='licence_bulkedit',
    ),
    url(
        r'^add/$',
        AddLicence.as_view(),
        name='add_licence',
    ),
    url(
        r'^edit/(?P<licence_id>[0-9]+)$',
        EditLicence.as_view(),
        name='edit_licence',
    ),
    url(
        r'^count/$',
        CountLicence.as_view(),
        name='count_licences',
    ),
)
