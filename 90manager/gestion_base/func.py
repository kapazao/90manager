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

from django.http import HttpResponseRedirect
from django.shortcuts import render


########################################################################

def redireccionar(direccion):
    """ Redirecciona a otra pagina web """
    return HttpResponseRedirect(direccion)


########################################################################

def devolver_mensaje(request, mensaje, tipo=0, url_salida=None):
    """ Devuelve un mensaje rapidamente como una pagina nueva
        Parametros:
        mensaje    -- mensaje a mostrar
        tipo       -- tipo de mensaje (0 - error, 1 - advertencia)
        url_salida -- url hacia la que redireccionar
    """

    if url_salida is None:
        url_salida = request.META.get('HTTP_REFERER')

    return generar_pagina(request, "mensaje.html", {"mensaje": mensaje, "url_salida": url_salida, "tipo": tipo})


########################################################################

def generar_pagina(request, template_name, parametros=None, agregar_parametros=True):
    """ Genera una pagina web con los templates añadiendo unos parámetros por defecto """
    if parametros is None:
        parametros = {}

    usuario = request.user

    if agregar_parametros:
        if usuario.is_authenticated():
            if 'liga_actual' in request.session:
                liga = request.session['liga_actual']
                parametros['liga_actual'] = liga
                notificaciones = usuario.notificacion_set.filter(liga=liga, leida=False)
                parametros['ultimas_notificaciones'] = notificaciones[:5]

                if liga.activada():
                    parametros['fecha_hora_liga'] = liga.get_fecha()
                    parametros['factor_tiempo'] = liga.factor_tiempo

                if 'equipo_propio' in request.session:
                    equipo = request.session['equipo_propio']
                    parametros['equipo_propio'] = equipo
            else:
                notificaciones = usuario.notificacion_set.filter(liga=None, leida=False)
                parametros['ultimas_notificaciones'] = notificaciones

            parametros['num_notificaciones'] = notificaciones.count()

    return render(request, template_name, parametros)


########################################################################

def quitar_acentos(cadena):
    cadena = cadena.replace('á', 'a')
    cadena = cadena.replace('é', 'e')
    cadena = cadena.replace('í', 'i')
    cadena = cadena.replace('ó', 'o')
    cadena = cadena.replace('ú', 'u')

    cadena = cadena.replace('Á', 'A')
    cadena = cadena.replace('É', 'E')
    cadena = cadena.replace('Í', 'I')
    cadena = cadena.replace('Ó', 'O')
    cadena = cadena.replace('Ú', 'U')

    return cadena


########################################################################

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

########################################################################
