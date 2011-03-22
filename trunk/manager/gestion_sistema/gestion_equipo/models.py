# -*- coding: utf-8 -*-
"""
Copyright 2011 by
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
from django.db import models
from django.db.models import Q, F

from gestion_sistema.gestion_liga.models import Liga
from gestion_usuario.models import Usuario

########################################################################

# Equipo
class Equipo(models.Model):
	''' Representa un equipo en el sistema '''
	nombre = models.CharField(max_length = 50)
	usuario = models.ForeignKey(Usuario, null = True)
	liga = models.ForeignKey(Liga)

	# Funciones
	def agregarJugador(self, jugador):
		''' Añade un jugador al equipo '''
		self.jugador_set.add(jugador)

	def getPartidos(self, liga):
		''' Devuelve los partidos de una liga en los que juega '''
		from gestion_sistema.gestion_partido.models import Partido
		q = Partido.objects.filter(Q(equipo_local = self) | Q(equipo_visitante = self))
		jornadas = list(liga.jornada_set.all())
		lista = q.filter(jornada__in = jornadas)
		return lista

	def getPartidosHastaJornada(self, jornada):
		''' Devuelve los partidos jugados hasta la jornada '''
		# Obtenemos la liga
		liga = jornada.liga
		# Obtenemos los partidos en los que juega
		partidos = self.getPartidos(liga)
		return partidos.filter(jornada__lt = jornada)

	def getPartidosGanados(self, jornada):
		''' Devuelve los partidos ganados hasta la jornada '''
		# Partidos hasta la jornada
		partidos = self.getPartidosHastaJornada(jornada)
		# Partidos jugados
		partidos_jugados = partidos.filter(jugado = True)
		# Partidos ganados como visitante
		partidos_ganados = partidos_jugados.filter(
			Q(Q(equipo_local = self) & Q(goles_local__gt = F('goles_visitante'))) |
			Q(Q(equipo_visitante = self) & Q(goles_local__lt = F('goles_visitante'))))
		return partidos_ganados

	def getPartidosPerdidos(self, jornada):
		''' Devuelve los partidos perdidos hasta la jornada '''
		# Partidos hasta la jornada
		partidos = self.getPartidosHastaJornada(jornada)
		# Partidos jugados
		partidos_jugados = partidos.filter(jugado = True)
		# Partidos perdidos como visitante
		partidos_perdidos = partidos_jugados.filter(
			Q(Q(equipo_local = self) & Q(goles_local__lt = F('goles_visitante'))) |
			Q(Q(equipo_visitante = self) & Q(goles_local__gt = F('goles_visitante'))))
		return partidos_perdidos

	def getPartidosEmpatados(self, jornada):
		''' Devuelve los partidos empatados hasta la jornada '''
		# Partidos hasta la jornada
		partidos = self.getPartidosHastaJornada(jornada)
		# Partidos jugados
		partidos_jugados = partidos.filter(jugado = True)
		# Partidos perdidos como visitante
		partidos_empatados = partidos_jugados.filter(goles_local = F('goles_visitante'))
		return partidos_empatados

	def generarJugadoresAleatorios(self, sexo_permitido = 1):
		''' Genera un conjunto de jugadores aleatorios para el equipo '''
		from gestion_sistema.gestion_jugador.models import Jugador
		from gestion_sistema.gestion_jugador.func import nombreJugadorAleatorio, listaNombres
		from datetime import date, timedelta
		from random import randint
		
		hombres_participan = False
		mujeres_participan = False
		
		num_jugadores_inicial = 25
		
		edad_min = 18
		edad_max = 35
		
		# Crear listas
		if sexo_permitido != 1: # Hombres participan
			hombres_participan = True
			lista_nombres_hombres = listaNombres("nombres_hombres.txt")
			max_nivel_hombres = 50
		
		if sexo_permitido != 0: # Mujeres participan
			mujeres_participan = True
			lista_nombres_mujeres = listaNombres("nombres_mujeres.txt")
			max_nivel_mujeres = 45
			
		lista_apellidos = listaNombres("apellidos.txt")

		# Generar jugadores
		for j in range(1, num_jugadores_inicial + 1):
			# Establecer posición
			if (j == 1 or j >= 24):
				posicion = "PORTERO"
			elif ((j >= 2 and j <= 5) or (j >= 12 and j <= 15)):
				posicion = "DEFENSA"
			elif ((j >= 6 and j <= 9) or (j >= 16 and j <= 19)):
				posicion = "CENTROCAMPISTA"
			else:
				posicion = "DELANTERO"
			
			# Obtener datos de hombre o mujer según si participan o no
			if ((j % 2 == 0) and hombres_participan) or (mujeres_participan == False):
				lista_nombres = lista_nombres_hombres
				max_nivel = max_nivel_hombres
				sexo = 'M'
			else:
				lista_nombres = lista_nombres_mujeres
				max_nivel = max_nivel_mujeres
				sexo = 'F'
			
			# Establecer variables del jugador	
			nombre_aleatorio, apodo_aux = nombreJugadorAleatorio(lista_nombres, lista_apellidos)
			fecha_nacimiento = date.today() - timedelta(randint(edad_min, edad_max) * 365) + timedelta(randint(0, 365))
			
			# Reducir un poco el nivel máximo dependiendo de la edad
			hoy = date.today()
			edad = hoy - fecha_nacimiento
			anios = (int)(edad.days / 365)
			
			# Cada 2 años de diferencia con 28 se resta un punto al nivel máximo
			max_nivel = max_nivel - (int)(abs(28 - anios) / 2)
			
			# Asignar variables al jugador
			jugador = Jugador(equipo = self, nombre = nombre_aleatorio, apodo = apodo_aux, fecha_nacimiento = fecha_nacimiento, sexo = sexo, transferible = False)
			jugador.setNumero(j)
			jugador.setHabilidadesAleatorias(posicion, max_nivel)
			jugador.setAparienciaAleatoria()
			
			# Guardar jugador
			jugador.save()
			
			# Añadir jugador al equipo
			self.agregarJugador(jugador)

	def __unicode__(self):
		return self.nombre

########################################################################
