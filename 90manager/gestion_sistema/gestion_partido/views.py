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
from django.db.models import Q

from gestion_base.func import devolver_mensaje, generar_pagina, redireccionar
from gestion_sistema.decorators import actualizar_liga, comprobar_sesion

from .forms import PrepararEquipoForm
from .models import JugadorPartido, Partido, Suceso


########################################################################

@login_required
def ver_partido_id(request, partido_id):
    """ Muestra los datos de un partido """

    partidos = Partido.objects.filter(id=partido_id)

    if partidos.count() == 0:
        return devolver_mensaje(request, "Error, no existe un partido con identificador %s" % partido_id)

    request.session['partido_actual'] = partidos[0]

    return redireccionar('/partidos/ver/')


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['partido_actual'])
def ver_partido(request):
    """ Muestra los datos de un partido """
    # Obtenemos el usuario
    usuario = request.user

    partido = request.session['partido_actual']

    # Obtener sucesos del partido
    partido.sucesos = partido.suceso_set.all()

    # Obtenemos la liga y la jornada
    jornada = partido.jornada
    liga = partido.liga

    # Obtenemos los equipos que juegan en el partido
    equipo_local = partido.equipo_local
    equipo_visitante = partido.equipo_visitante

    # Comprobar si tiene equipo en el partido y se puede editar la alineación
    editar = False
    tiene_equipo = False

    if equipo_local.usuario == usuario:
        tiene_equipo = True
        if partido.alineacion_local.esta_preparada():
            editar = True
    elif equipo_visitante.usuario == usuario:
        tiene_equipo = True
        if partido.alineacion_visitante.esta_preparada():
            editar = True

    es_creador = liga.creador == usuario

    # Comprobamos si el partido ha acabado
    finalizado = partido.finalizado()

    # Comprobar si se puede jugar el partido
    es_jugable = False
    jornada_actual = liga.get_jornada_actual()
    if partido.jornada == jornada_actual and not finalizado:
        es_jugable = True

    # Si el partido ha finalizado
    if finalizado:
        # Obtener datos sobre los sucesos del partido
        for equipo in (equipo_local, equipo_visitante):
            sucesos = partido.suceso_set.filter(equipo=equipo)
            equipo.num_acciones = sucesos.count()

            # Regates
            equipo.regates_realizados = sucesos.filter(tipo=Suceso.REGATE, valor=1).count()
            equipo.regates_fallados = sucesos.filter(tipo=Suceso.REGATE, valor=0).count()

            if equipo.regates_realizados + equipo.regates_fallados == 0:
                equipo.porcentaje_regates_exito = 0
            else:
                equipo.porcentaje_regates_exito = (1.0 * equipo.regates_realizados) / (
                    equipo.regates_realizados + equipo.regates_fallados)

            equipo.regates_totales = equipo.regates_realizados + equipo.regates_fallados

            # Pases
            equipo.pases_realizados = sucesos.filter(tipo=Suceso.PASE, valor=1).count()
            equipo.pases_fallados = sucesos.filter(tipo=Suceso.PASE, valor=0).count()

            if equipo.pases_realizados + equipo.pases_fallados == 0:
                equipo.porcentaje_pases_exito = 0
            else:
                equipo.porcentaje_pases_exito = (1.0 * equipo.pases_realizados) / (
                    equipo.pases_realizados + equipo.pases_fallados)

            equipo.pases_totales = equipo.pases_realizados + equipo.pases_fallados

            # Disparos
            equipo.disparos_parados = sucesos.filter(tipo=Suceso.DISPARO, valor=1).count()
            equipo.disparos_fuera = sucesos.filter(tipo=Suceso.DISPARO, valor=0).count()
            equipo.goles = sucesos.filter(tipo=Suceso.GOL).count()
            equipo.disparos_a_puerta = equipo.goles + equipo.disparos_parados
            equipo.disparos_totales = equipo.disparos_a_puerta + equipo.disparos_fuera

            equipo.balones_perdidos = \
                equipo.regates_fallados + equipo.pases_fallados + \
                equipo.disparos_parados + equipo.disparos_fuera

        equipo_local.balones_recuperados = \
            equipo_visitante.regates_fallados + \
            equipo_visitante.pases_fallados + \
            equipo_visitante.disparos_parados

        equipo_visitante.balones_recuperados = \
            equipo_local.regates_fallados + \
            equipo_local.pases_fallados + \
            equipo_local.disparos_parados
        # --------------------------------------------------

        # Porcentajes
        num_acciones_total = equipo_local.num_acciones + equipo_visitante.num_acciones

        if num_acciones_total > 0:
            for equipo in (equipo_local, equipo_visitante):
                equipo.porc_posesion = 0 \
                    if (num_acciones_total == 0) \
                    else round((100.0 * equipo.num_acciones) / num_acciones_total, 1)
                equipo.porc_regates_exito = 0 \
                    if (equipo.regates_totales == 0) \
                    else round((100.0 * equipo.regates_realizados) / equipo.regates_totales, 1)
                equipo.porc_pases_exito = 0 \
                    if (equipo.pases_totales == 0) \
                    else round((100.0 * equipo.pases_realizados) / equipo.pases_totales, 1)
                equipo.porc_disparos_exito = 0 \
                    if (equipo.disparos_totales == 0) \
                    else round((100.0 * equipo.disparos_a_puerta) / equipo.disparos_totales, 1)

            for equipo, alineacion in (
                    (equipo_local, partido.alineacion_local), (equipo_visitante, partido.alineacion_visitante)):
                # Obtener datos de los titulares del equipo
                equipo.titulares = alineacion.get_datos_titulares()

                equipo.suma_nivel_titulares = 0
                equipo.num_df = 0
                equipo.num_cc = 0
                equipo.num_dl = 0
                for t in equipo.titulares:
                    # Valor total del equipo
                    equipo.suma_nivel_titulares += t.atributos.get_nivel()

                    # Número de jugadores por posición
                    if t.posicion == JugadorPartido.DEFENSA:
                        equipo.num_df += 1
                    elif t.posicion == JugadorPartido.CENTROCAMPISTA:
                        equipo.num_cc += 1
                    elif t.posicion == JugadorPartido.DELANTERO:
                        equipo.num_dl += 1

                equipo.nivel_medio_titulares = "%.2f" % (1.0 * equipo.suma_nivel_titulares / len(equipo.titulares))

    sucesos = partido.suceso_set.filter(
        Q(tipo=Suceso.GOL) |
        Q(tipo=Suceso.DISPARO) |
        Q(tipo=Suceso.FIN_PARTE) |
        Q(tipo=Suceso.TIEMPO_DESCUENTO) |
        Q(tipo=Suceso.COMENZAR)
    )

    d = {
        "jornada": jornada,
        "equipo_local": equipo_local,
        "equipo_visitante": equipo_visitante,
        "liga": liga,
        "partido": partido,
        "usuario": usuario,
        "finalizado": finalizado,
        "es_creador": es_creador,
        "tiene_equipo": tiene_equipo,
        "es_jugable": es_jugable,
        "editar": editar,
        "sucesos": sucesos,
    }

    return generar_pagina(request, "juego/partidos/ver_partido.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['partido_actual'])
def preparar_partido(request):
    """ Muestra los datos para preparar un partido """
    usuario = request.user

    partido = request.session['partido_actual']

    # Comprobar que el partido no se haya jugado ya
    if partido.finalizado():
        return devolver_mensaje(request, "Este partido ya acabo", 0, "/partidos/ver/%d/" % partido.id)

    # Comprobar si el usuario juega en el partido
    if partido.equipo_local.usuario == usuario:  # Juega como local
        equipo = partido.equipo_local
        alineacion = partido.alineacion_local
    elif partido.equipo_visitante.usuario == usuario:  # Juega como visitante
        equipo = partido.equipo_visitante
        alineacion = partido.alineacion_visitante
    else:  # No juega como naaaaaaaaaaaaaaa
        return devolver_mensaje(request, "No tienes equipo en este partido", 0, "/partidos/ver/%d/" % partido.id)

    editar = alineacion.esta_preparada()

    if request.method == 'POST':
        form = PrepararEquipoForm(alineacion, equipo, request.POST)

        if form.is_valid():
            delanteros = form.cleaned_data['delanteros']
            centrocampistas = form.cleaned_data['centrocampistas']
            defensas = form.cleaned_data['defensas']
            portero = form.cleaned_data['portero']
            suplentes = form.cleaned_data['suplentes']
            alineacion.set_alineacion(portero, defensas, centrocampistas, delanteros, suplentes)
            alineacion.save()
            # Preparar la alineacion perfectamente
            if editar:
                return devolver_mensaje(request, "Se ha editado correctamente la alineacion", 1,
                                        "/partidos/ver/%d/" % partido.id)
            else:
                return devolver_mensaje(request, "Se ha creado correctamente la alineacion", 1,
                                        "/partidos/ver/%d/" % partido.id)
    else:
        form = PrepararEquipoForm(alineacion, equipo)

    delanteros = alineacion.get_delanteros()
    centrocampistas = alineacion.get_centrocampistas()
    defensas = alineacion.get_defensas()
    portero = alineacion.get_portero()
    suplentes = alineacion.get_suplentes()

    jugadores = equipo.get_jugadores()

    d = {
        "form": form,
        "editar": editar,
        "partido": partido,
        "equipo": equipo,
        "jugadores": jugadores,
        "delanteros": delanteros,
        "defensas": defensas,
        "portero": portero,
        "centrocampistas": centrocampistas,
        "suplentes": suplentes
    }

    return generar_pagina(request, "juego/partidos/preparar_partido.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['partido_actual'])
def ver_repeticion_partido(request):
    """ Muestra la repeticion de un partido """

    # Obtenemos el partido
    partido = request.session['partido_actual']

    # Obtener sucesos del partido
    sucesos = partido.suceso_set.all()

    # Obtenemos la liga y la jornada
    jornada = partido.jornada
    liga = jornada.liga

    # Obtenemos los equipos que juegan en el partido
    equipo_local = partido.equipo_local
    equipo_visitante = partido.equipo_visitante

    # Comprobamos si el partido ha acabado
    finalizado = partido.finalizado()

    # Si el partido ha finalizado
    if not finalizado:
        return devolver_mensaje(request, "Error, el partido no acabó", 0, "/partidos/ver/%d/" % partido.id)

    siglas_local = equipo_local.siglas
    siglas_visitante = equipo_visitante.siglas

    d = {
        "jornada": jornada,
        "liga": liga,
        "partido": partido,
        "sucesos": sucesos,
        "siglas_local": siglas_local,
        "siglas_visitante": siglas_visitante
    }

    return generar_pagina(request, "juego/partidos/ver_repeticion_partido.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual', 'equipo_propio'])
def ver_partidos_propios(request):
    """ Accede directamente al siguiente partido """

    liga = request.session['liga_actual']
    equipo = request.session['equipo_propio']

    partidos = liga.partido_set.filter(Q(equipo_local=equipo) | Q(equipo_visitante=equipo))

    # Obtener partido actual
    partidos_no_jugados = partidos.filter(jugado=False)

    if partidos_no_jugados.count() > 0:
        partido_actual = partidos_no_jugados[0]
    else:
        partido_actual = None

    # Generar página
    d = {
        "partido_actual": partido_actual,
        "partidos": partidos,
    }

    return generar_pagina(request, "juego/partidos/listar_partidos_equipo.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual', 'equipo_propio'])
def proximo_partido(request):
    """ Accede directamente al siguiente partido """
    liga = request.session['liga_actual']
    equipo = request.session['equipo_propio']

    partidos = liga.partido_set.filter(jugado=False).filter(Q(equipo_local=equipo) | Q(equipo_visitante=equipo))

    if partidos.count() > 0:
        partido_actual = partidos[0]
    else:
        return devolver_mensaje(request, "Error, no hay mas partidos por jugar en la liga", 0)

    return redireccionar('/partidos/ver/%s/' % partido_actual.id)

########################################################################
