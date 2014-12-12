# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from ralph_assets.rest import (
    AssetInfoPerRackAPIView,
    DCRacksAPIView,
)


urlpatterns = patterns(
    '',
    url(
        r'^rack/(?P<rack_id>\d+)/$',
        AssetInfoPerRackAPIView.as_view(),
    ),
    url(
        r'^data_center/(?P<data_center_id>\d+)/$',
        DCRacksAPIView.as_view(),
    ),
)
