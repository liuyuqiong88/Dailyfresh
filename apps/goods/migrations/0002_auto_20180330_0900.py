# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goodsimage',
            options={'verbose_name': '商品图片', 'verbose_name_plural': '商品图片'},
        ),
        migrations.RenameField(
            model_name='goodssku',
            old_name='print',
            new_name='price',
        ),
    ]
