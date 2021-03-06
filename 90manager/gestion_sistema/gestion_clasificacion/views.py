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

# Vistas del sistema
from django.contrib.auth.decorators import login_required

from gestion_base.func import generar_pagina, quitar_acentos
from gestion_sistema.decorators import comprobar_sesion


########################################################################

@login_required
@comprobar_sesion(['liga_actual'])
def ver_clasificacion(request):
    """ Muestra la clasificacion actual del sistema """

    liga = request.session['liga_actual']

    # Obtenemos las jornadas
    jornadas = liga.get_jornadas()
    jornada_actual = liga.get_jornada_actual()
    jornada_anterior = None

    clasificacion = None

    # Si la liga ha acabado
    if not jornada_actual:
        liga_acabada = True
    else:
        liga_acabada = False

        if jornada_actual.numero >= 2:
            jornada_anterior = jornadas.get(numero=jornada_actual.numero)
            clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
            clasificacion = sorted(clasificacion_sin_ordenar, key=lambda dato: (
                -dato.puntos, -(dato.goles_favor - dato.goles_contra), -dato.goles_favor))
        elif jornada_actual.numero == 1:  # Generar clasificacion vacía
            clasificacion = jornada_actual.clasificacionequipojornada_set.all()
            clasificacion = sorted(clasificacion, key=lambda dato: quitar_acentos(dato.equipo.nombre.lower()))

    if liga_acabada:
        jornada_anterior = jornadas[liga.get_num_jornadas() - 1]
        clasificacion_sin_ordenar = jornada_anterior.clasificacionequipojornada_set.all()
        clasificacion = sorted(clasificacion_sin_ordenar, key=lambda dato: (
            -dato.puntos, -(dato.goles_favor - dato.goles_contra), -dato.goles_favor))

    if clasificacion is not None:
        # Calcular variables extra para la clasificación
        posicion = 1

        ultima_posicion_ascenso = 1
        primera_posicion_descenso = len(clasificacion)

        for c in clasificacion:
            c.posicion = posicion

            # Comprobar si es posición de ascenso
            if c.posicion <= ultima_posicion_ascenso:
                c.posicion_ascenso = True
            else:
                c.posicion_ascenso = False

            # Comprobar si es posición de descenso
            if c.posicion >= primera_posicion_descenso:
                c.posicion_descenso = True
            else:
                c.posicion_descenso = False

            c.goles_diferencia = c.goles_favor - c.goles_contra

            if jornada_anterior is not None:
                incluida = True

                if not liga_acabada:
                    jornada_a_comprobar = jornada_actual
                else:
                    jornada_a_comprobar = jornada_anterior
                    incluida = True

                c.partidos_ganados = len(c.equipo.get_partidos_ganados(jornada_a_comprobar, incluida))
                c.partidos_empatados = len(c.equipo.get_partidos_empatados(jornada_a_comprobar, incluida))
                c.partidos_perdidos = len(c.equipo.get_partidos_perdidos(jornada_a_comprobar, incluida))

            else:
                c.partidos_ganados = len(c.equipo.get_partidos_ganados(jornada_actual, True))
                c.partidos_empatados = len(c.equipo.get_partidos_empatados(jornada_actual, True))
                c.partidos_perdidos = len(c.equipo.get_partidos_perdidos(jornada_actual, True))

            c.partidos_jugados = c.partidos_ganados + c.partidos_empatados + c.partidos_perdidos

            posicion += 1

    # Cargamos la plantilla con los parametros y la devolvemos
    d = {
        "liga": liga,
        "clasificacion": clasificacion,
        "jornada_actual": jornada_actual,
    }

    return generar_pagina(request, "juego/clasificaciones/ver_liga.html", d)

########################################################################
