# -*- coding: utf-8 -*-
"""
Copyright 2017 by
    * Juan Miguel Lechuga Pérez
    * Jose Luis López Pino
    * Carlos Antonio Rivera Cabello

 This file is part of 90Manager.

    90Manager is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    90Manager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 90Manager.  If not, see <http://www.gnu.org/licenses/>.

"""

from django.conf.urls import url

from gestion_mercado.gestion_subasta import views

urlpatterns = [
    # Modulo de subastas
    url(r'^ver/liga/$', views.ver_subastas_liga),
    url(r'^ver/equipo/$', views.ver_subastas_equipo),
    url(r'^ver/(?P<subasta_id>\d+)/$', views.ver_subasta_id),
    url(r'^ver/$', views.ver_subasta),
    url(r'^comprar/$', views.comprar_subasta),
    url(r'^crear/$', views.crear_subasta),
    url(r'^propias/$', views.mis_subastas),
    url(r'^pujas/$', views.mis_pujas),
]
