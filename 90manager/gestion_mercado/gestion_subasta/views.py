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
from django.db import transaction

from gestion_base.func import devolver_mensaje, generar_pagina, redireccionar
from gestion_sistema.decorators import actualizar_liga, comprobar_sesion

from .forms import PujarForm, SubastaForm
from .models import Subasta


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['jugador_actual'])
@transaction.atomic
def crear_subasta(request):
    """ Crea una subasta de un jugador """
    usuario = request.user

    jugador = request.session['jugador_actual']

    if not jugador.atributos.equipo.liga.activada():
        return devolver_mensaje(request, "La liga no esta activada y no hay mercado aun", 0)

    if jugador.atributos.ofertado:
        return devolver_mensaje(request, "Este jugador ya está en subasta", 0, "/jugadores/ver/%d/" % jugador.id)

    if jugador.atributos.equipo.usuario != usuario:
        return devolver_mensaje(request, "No eres propietario del equipo del jugador", 0)

    if not jugador.atributos.equipo.liga.activada():
        return devolver_mensaje(request, "Hasta que la liga no esté activada no pueden haber subastas", 0)

    duracion_liga = jugador.atributos.equipo.liga.get_num_jornadas()

    if request.method == 'POST':
        form = SubastaForm(jugador, request.POST)
        if form.is_valid():
            subasta = form.save(commit=False)

            # comision = subasta.puja * (subasta.getTiempoRestante().days() / (duracion_liga * 1.0))
            comision = 10
            if comision > jugador.atributos.equipo.dinero:
                return devolver_mensaje(request, "No tienes suficiente dinero para pagar la comision", 0,
                                        "/mercado/subastas/crear/%d/" % jugador.id)

            subasta.liga = jugador.atributos.equipo.liga
            subasta.fecha_inicio = subasta.liga.get_fecha()
            subasta.estado = 0
            subasta.vendedor = jugador.atributos.equipo
            subasta.comprador = None
            subasta.atributos_jugador = jugador.atributos

            jugador.atributos.equipo.cobrar(comision)

            jugador.atributos.ofertado = True
            jugador.atributos.save()
            subasta.save()
            return devolver_mensaje(request, "Se ha creado correctamente", 1, "/mercado/subastas/ver/%d/" % subasta.id)
    else:
        form = SubastaForm(jugador)

    d = {
        "form": form,
        "jugador": jugador,
        "duracion_liga": duracion_liga
    }

    return generar_pagina(request, "juego/subastas/crear_subasta.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['liga_actual'])
def ver_subastas_liga(request):
    """ Muestra las subastas de una liga """
    liga = request.session['liga_actual']

    # Comprobamos que la liga este activada
    if not liga.activada():
        return devolver_mensaje(request, "La liga no esta activada y no hay mercado aun", 0)

    subastas = liga.subasta_set.all()

    return generar_pagina(request, "juego/subastas/ver_subastas_liga.html", {"subastas": subastas, "liga": liga})


########################################################################

@login_required
def ver_subasta_id(request, subasta_id):
    """ Muestra los datos de una subasta """
    subastas = Subasta.objects.filter(id=subasta_id)
    if subastas.count() == 0:
        return devolver_mensaje(request, "Error, no existe una subasta con identificador %s" % subasta_id, 0)

    request.session['subasta_actual'] = subastas[0]

    return redireccionar('/mercado/subastas/ver/')


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['subasta_actual'])
def ver_subasta(request):
    """ Muestra los datos de una subasta """
    # Obtenemos el usuario
    usuario = request.user

    # Obtenemos la subasta
    subasta = request.session['subasta_actual']

    # Equipo del usuario
    equipo_usuario = None
    form = None
    if usuario.equipo_set.filter(liga=subasta.liga).count():
        equipo_usuario = usuario.equipo_set.get(liga=subasta.liga)

    if subasta.vendedor != equipo_usuario:
        if request.method == 'POST':
            if not equipo_usuario:
                devolver_mensaje(request, 'No puedes pujar en una liga en la que no juegas', 0)
            form = PujarForm(subasta, equipo_usuario, request.POST)
            if form.is_valid():
                cantidad = form.cleaned_data['cantidad']
                subasta.pujar(equipo_usuario, cantidad)
                subasta.save()
                print(cantidad, subasta.puja)
                return devolver_mensaje(request, "Cantidad apostada correctamente", 1,
                                        "/mercado/subastas/ver/%d/" % subasta.id)
        else:
            form = PujarForm(subasta, equipo_usuario)

    d = {
        "equipo_usuario": equipo_usuario,
        "subasta": subasta,
        "form": form,
    }

    return generar_pagina(request, "juego/subastas/ver_subasta.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['equipo_actual'])
def ver_subastas_equipo(request):
    """ Muestra las subastas de un equipo """
    equipo = request.session['equipo_actual']

    # Comprobamos que la liga este activada
    if not equipo.liga.activada():
        return devolver_mensaje(request, "La liga no esta activada y no hay mercado aun", 0)

    subastas_comprador = equipo.subastas_como_comprador.all()
    subastas_vendedor = equipo.subastas_como_vendedor.all()

    d = {
        "subastas_comprador": subastas_comprador,
        "subastas_vendedor": subastas_vendedor,
        "equipo": equipo,
    }

    return generar_pagina(request, "juego/subastas/ver_subastas_equipo.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['subasta_actual'])
def comprar_subasta(request):
    """ Muestra los datos de una subasta """
    # Obtenemos el usuario
    usuario = request.user

    # Obtenemos la subasta
    subasta = request.session['subasta_actual']

    # Comprobamos que la liga este activada
    if not subasta.liga.activada():
        return devolver_mensaje(request, "La liga no esta activada y no hay mercado aun", 0)

    if not usuario.equipo_set.filter(liga=subasta.liga).count():
        return devolver_mensaje(request, "Error, no tienes equipo en esta liga", 0)

    if subasta.estado is not 0:
        return devolver_mensaje(request, "Error, la subasta %s ya acabó" % subasta.id, 0)

    if not subasta.precio_compra:
        return devolver_mensaje(request, "Error, la subasta %s no puede comprarse directamente" % subasta.id, 0)

    equipo = usuario.equipo_set.get(liga=subasta.liga)

    if subasta.vendedor == equipo:
        return devolver_mensaje(request, "Error, no puedes comprarte tu propia subasta", 0)

    if subasta.precio_compra > equipo.dinero:
        return devolver_mensaje(request, "Error, no tienes dinero para comprar esta subasta", 0,
                                "/mercado/subastas/ver/%s/" % subasta.id)

    # Burocracia de comprar al jugador
    subasta.comprar(equipo)
    subasta.save()

    return devolver_mensaje(request, "Ha comprado al jugador correctamente", 1,
                            "/mercado/subastas/ver/%s/" % subasta.id)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['equipo_propio'])
def mis_subastas(request):
    """ Muestra las subastas de un equipo """
    equipo = request.session['equipo_propio']

    # Comprobamos que la liga este activada
    if not equipo.liga.activada():
        return devolver_mensaje(request, "La liga no esta activada y no hay mercado aún", 0)

    subastas = equipo.subastas_como_vendedor.all()

    d = {
        "subastas": subastas,
    }

    return generar_pagina(request, "juego/subastas/mis_subastas.html", d)


########################################################################

@login_required
@actualizar_liga
@comprobar_sesion(['equipo_propio'])
def mis_pujas(request):
    """ Muestra las subastas de un equipo """
    equipo = request.session['equipo_propio']

    # Comprobamos que la liga este activada
    if not equipo.liga.activada():
        return devolver_mensaje(request, "La liga no esta activada y no hay mercado aún", 0)

    subastas = equipo.subastas_como_comprador.all()

    d = {
        "subastas": subastas,
    }

    return generar_pagina(request, "juego/subastas/mis_pujas.html", d)

########################################################################
