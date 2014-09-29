# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.forms.models import modelformset_factory


ISO_3166 = (
    ('AF', 'AFG'), ('AX', 'ALA'), ('AL', 'ALB'), ('DZ', 'DZA'), ('AS', 'ASM'),
    ('AD', 'AND'), ('AO', 'AGO'), ('AI', 'AIA'), ('AQ', 'ATA'), ('AG', 'ATG'),
    ('AR', 'ARG'), ('AM', 'ARM'), ('AW', 'ABW'), ('AU', 'AUS'), ('AT', 'AUT'),
    ('AZ', 'AZE'), ('BS', 'BHS'), ('BH', 'BHR'), ('BD', 'BGD'), ('BB', 'BRB'),
    ('BY', 'BLR'), ('BE', 'BEL'), ('BZ', 'BLZ'), ('BJ', 'BEN'), ('BM', 'BMU'),
    ('BT', 'BTN'), ('BO', 'BOL'), ('BQ', 'BES'), ('BA', 'BIH'), ('BW', 'BWA'),
    ('BV', 'BVT'), ('BR', 'BRA'), ('IO', 'IOT'), ('BN', 'BRN'), ('BG', 'BGR'),
    ('BF', 'BFA'), ('BI', 'BDI'), ('KH', 'KHM'), ('CM', 'CMR'), ('CA', 'CAN'),
    ('CV', 'CPV'), ('KY', 'CYM'), ('CF', 'CAF'), ('TD', 'TCD'), ('CL', 'CHL'),
    ('CN', 'CHN'), ('CX', 'CXR'), ('CC', 'CCK'), ('CO', 'COL'), ('KM', 'COM'),
    ('CG', 'COG'), ('CD', 'COD'), ('CK', 'COK'), ('CR', 'CRI'), ('CI', 'CIV'),
    ('HR', 'HRV'), ('CU', 'CUB'), ('CW', 'CUW'), ('CY', 'CYP'), ('CZ', 'CZE'),
    ('DK', 'DNK'), ('DJ', 'DJI'), ('DM', 'DMA'), ('DO', 'DOM'), ('EC', 'ECU'),
    ('EG', 'EGY'), ('SV', 'SLV'), ('GQ', 'GNQ'), ('ER', 'ERI'), ('EE', 'EST'),
    ('ET', 'ETH'), ('FK', 'FLK'), ('FO', 'FRO'), ('FJ', 'FJI'), ('FI', 'FIN'),
    ('FR', 'FRA'), ('GF', 'GUF'), ('PF', 'PYF'), ('TF', 'ATF'), ('GA', 'GAB'),
    ('GM', 'GMB'), ('GE', 'GEO'), ('DE', 'DEU'), ('GH', 'GHA'), ('GI', 'GIB'),
    ('GR', 'GRC'), ('GL', 'GRL'), ('GD', 'GRD'), ('GP', 'GLP'), ('GU', 'GUM'),
    ('GT', 'GTM'), ('GG', 'GGY'), ('GN', 'GIN'), ('GW', 'GNB'), ('GY', 'GUY'),
    ('HT', 'HTI'), ('HM', 'HMD'), ('VA', 'VAT'), ('HN', 'HND'), ('HK', 'HKG'),
    ('HU', 'HUN'), ('IS', 'ISL'), ('IN', 'IND'), ('ID', 'IDN'), ('IR', 'IRN'),
    ('IQ', 'IRQ'), ('IE', 'IRL'), ('IM', 'IMN'), ('IL', 'ISR'), ('IT', 'ITA'),
    ('JM', 'JAM'), ('JP', 'JPN'), ('JE', 'JEY'), ('JO', 'JOR'), ('KZ', 'KAZ'),
    ('KE', 'KEN'), ('KI', 'KIR'), ('KP', 'PRK'), ('KR', 'KOR'), ('KW', 'KWT'),
    ('KG', 'KGZ'), ('LA', 'LAO'), ('LV', 'LVA'), ('LB', 'LBN'), ('LS', 'LSO'),
    ('LR', 'LBR'), ('LY', 'LBY'), ('LI', 'LIE'), ('LT', 'LTU'), ('LU', 'LUX'),
    ('MO', 'MAC'), ('MK', 'MKD'), ('MG', 'MDG'), ('MW', 'MWI'), ('MY', 'MYS'),
    ('MV', 'MDV'), ('ML', 'MLI'), ('MT', 'MLT'), ('MH', 'MHL'), ('MQ', 'MTQ'),
    ('MR', 'MRT'), ('MU', 'MUS'), ('YT', 'MYT'), ('MX', 'MEX'), ('FM', 'FSM'),
    ('MD', 'MDA'), ('MC', 'MCO'), ('MN', 'MNG'), ('ME', 'MNE'), ('MS', 'MSR'),
    ('MA', 'MAR'), ('MZ', 'MOZ'), ('MM', 'MMR'), ('NA', 'NAM'), ('NR', 'NRU'),
    ('NP', 'NPL'), ('NL', 'NLD'), ('NC', 'NCL'), ('NZ', 'NZL'), ('NI', 'NIC'),
    ('NE', 'NER'), ('NG', 'NGA'), ('NU', 'NIU'), ('NF', 'NFK'), ('MP', 'MNP'),
    ('NO', 'NOR'), ('OM', 'OMN'), ('PK', 'PAK'), ('PW', 'PLW'), ('PS', 'PSE'),
    ('PA', 'PAN'), ('PG', 'PNG'), ('PY', 'PRY'), ('PE', 'PER'), ('PH', 'PHL'),
    ('PN', 'PCN'), ('PL', 'POL'), ('PT', 'PRT'), ('PR', 'PRI'), ('QA', 'QAT'),
    ('RE', 'REU'), ('RO', 'ROU'), ('RU', 'RUS'), ('RW', 'RWA'), ('BL', 'BLM'),
    ('SH', 'SHN'), ('KN', 'KNA'), ('LC', 'LCA'), ('MF', 'MAF'), ('PM', 'SPM'),
    ('VC', 'VCT'), ('WS', 'WSM'), ('SM', 'SMR'), ('ST', 'STP'), ('SA', 'SAU'),
    ('SN', 'SEN'), ('RS', 'SRB'), ('SC', 'SYC'), ('SL', 'SLE'), ('SG', 'SGP'),
    ('SX', 'SXM'), ('SK', 'SVK'), ('SI', 'SVN'), ('SB', 'SLB'), ('SO', 'SOM'),
    ('ZA', 'ZAF'), ('GS', 'SGS'), ('SS', 'SSD'), ('ES', 'ESP'), ('LK', 'LKA'),
    ('SD', 'SDN'), ('SR', 'SUR'), ('SJ', 'SJM'), ('SZ', 'SWZ'), ('SE', 'SWE'),
    ('CH', 'CHE'), ('SY', 'SYR'), ('TW', 'TWN'), ('TJ', 'TJK'), ('TZ', 'TZA'),
    ('TH', 'THA'), ('TL', 'TLS'), ('TG', 'TGO'), ('TK', 'TKL'), ('TO', 'TON'),
    ('TT', 'TTO'), ('TN', 'TUN'), ('TR', 'TUR'), ('TM', 'TKM'), ('TC', 'TCA'),
    ('TV', 'TUV'), ('UG', 'UGA'), ('UA', 'UKR'), ('AE', 'ARE'), ('GB', 'GBR'),
    ('US', 'USA'), ('UM', 'UMI'), ('UY', 'URY'), ('UZ', 'UZB'), ('VU', 'VUT'),
    ('VE', 'VEN'), ('VN', 'VNM'), ('VG', 'VGB'), ('VI', 'VIR'), ('WF', 'WLF'),
    ('EH', 'ESH'), ('YE', 'YEM'), ('ZM', 'ZMB'), ('ZW', 'ZWE')
)

iso2_to_iso3 = {k: v for k, v in ISO_3166}
iso3_to_iso2 = {v: k for k, v in ISO_3166}


class IntegerWidget(forms.TextInput):
    input_type = 'number'


def assigned_formset_factory(obj, base_model, field, lookup,
                             extra=1, extra_exclude=None):
    obj_class_name = obj.__class__.__name__.lower()
    if obj_class_name == field:
        raise Exception('Nie można podawać takich samych pól')
    if obj.__class__ == base_model:
        raise Exception('Nie można podawać takich samych modeli')

    class Form(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(Form, self).__init__(*args, **kwargs)
            self.fields[field] = AutoCompleteSelectField(lookup, required=True)
            self.fields[obj.__class__.__name__.lower()] = forms.IntegerField(widget=forms.HiddenInput(), initial=obj.id)  # noqa
            self.fields['delete'] = forms.BooleanField(
                required=False,
                widget=forms.CheckboxInput(),
            )
            self.fields['quantity'] = forms.IntegerField(
                min_value=1,
                widget=IntegerWidget(attrs={
                    'type': 'number',
                    'min': 1,
                    'step': 1,
                    'class': 'licence-count-input',
                }),
                initial=1,
            )

        class Meta:
            model = base_model
            exclude = extra_exclude or []

        def clean(self):
            data_cleaned = super(Form, self).clean()
            data_cleaned['licence'] = obj
            return data_cleaned
            # import ipdb; ipdb.set_trace()

    formset = modelformset_factory(
        model=base_model,
        form=Form,
        extra=extra,
        can_delete=False,
    )
    return formset
