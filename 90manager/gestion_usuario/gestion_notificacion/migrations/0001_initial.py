# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 16:23
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gestion_liga', '0001_initial'),
        ('gestion_usuario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.PositiveIntegerField(choices=[(100, 'Liga activada'), (300, 'Subasta finalizada'), (301, 'Subasta ganada'), (302, 'Subasta superada'), (303, 'Subasta superada mediante compra'), (400, 'Partido finalizado')], default=0)),
                ('identificador', models.PositiveIntegerField()),
                ('leida', models.BooleanField(default=False)),
                ('fecha_emision', models.DateTimeField()),
                ('liga', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gestion_liga.Liga')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestion_usuario.Usuario')),
            ],
        ),
    ]
