# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from django.db.models import Q

from ralph_assets.models_assets import Asset, Warehouse


logger = logging.getLogger(__name__)


def get_warehouses():
    """Yields dicts describing all warehouses"""
    for warehouse in Warehouse.objects.all():
        yield {
            'warehouse_id': warehouse.id,
            'warehouse_name': warehouse.name,
        }


def get_assets(date):
    """Yields dicts describing all assets"""
    for asset in Asset.objects_dc.filter(
        Q(invoice_date=None) | Q(invoice_date__lte=date),
        part_info=None,
    ):
        device_info = asset.device_info
        if not asset.warehouse:
            logger.error('Asset {0} has no warehouse'.format(asset.id))
            continue
        if not asset.model:
            logger.error('Asset {0} has no model'.format(asset.id))
            continue
        if not asset.device_info:
            logger.error('Asset {0} has no device'.format(asset.id))
            continue
        if not asset.service:
            logger.error('Asset {0} has no service'.format(asset.id))
            continue
        if not asset.device_environment:
            logger.error('Asset {0} has no environment'.format(asset.id))
            continue
        else:
            hostname = None
            if device_info:
                ralph_device = device_info.get_ralph_device()
                if ralph_device:
                    hostname = ralph_device.name

        yield {
            'asset_id': asset.id,
            'device_id': device_info.ralph_device_id if device_info else None,
            'asset_name': hostname,
            'service_ci_uid': asset.service.uid,
            'environment_id': asset.device_environment.id,
            'sn': asset.sn,
            'barcode': asset.barcode,
            'warehouse_id': asset.warehouse.id,
            'cores_count': asset.cores_count,
            'power_consumption': asset.model.power_consumption,
            'collocation': asset.model.height_of_device,
            'depreciation_rate': asset.deprecation_rate,
            'is_depreciated': asset.is_deprecated(date=date),
            'price': asset.price,
        }


def get_asset_parts():
    """Yields dicts describing parts of assets"""
    for asset in Asset.objects_dc.all():
        for part in asset.get_parts():
            device_info = asset.device_info
            yield {
                'asset_id': part.id,
                'barcode': asset.barcode,
                'is_deprecated': part.is_deprecated(),
                'model': part.model.name if part.model else None,
                'price': part.price,
                'ralph_id': device_info.ralph_device_id if device_info else None,  # noqa
                'sn': asset.sn,
                'deprecation_rate': asset.deprecation_rate,
                'is_deprecated': part.is_deprecated(),
            }
