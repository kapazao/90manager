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

from gestion_sistema.gestion_equipo.models import Equipo
from gestion_sistema.gestion_jugador.models import Jugador
from gestion_sistema.gestion_jornada.models import Jornada

from random import randint
from func import probabilidadExito

POSICIONES = (
	('BA', 'BANQUILLO'),
	('PO', 'PORTERO'),
	('DF', 'DEFENSA'),
	('CC', 'CENTROCAMPISTA'),
	('DL', 'DELANTERO'),
)

########################################################################

class JugadorPartido(models.Model):
	''' Representa los atributos de un jugador en un partido '''
	jugador = models.ForeignKey(Jugador)
	posicion = models.CharField(max_length = 2, choices = POSICIONES)

	ataque = models.IntegerField(null = False, blank = False)
	defensa = models.IntegerField(null = False, blank = False)
	velocidad = models.IntegerField(null = False, blank = False)
	pases = models.IntegerField(null = False, blank = False)
	anotacion = models.IntegerField(null = False, blank = False)
	portero = models.IntegerField(null = False, blank = False)

	def __init__(self, *args, **kwargs):
		super(JugadorPartido, self).__init__(*args, **kwargs)
		self.ataque = self.jugador.ataque
		self.defensa = self.jugador.defensa
		self.velocidad = self.jugador.velocidad
		self.pases = self.jugador.pases
		self.anotacion = self.jugador.anotacion
		self.portero = self.jugador.portero

	def __unicode__(self):
		''' Devuelve una cadena representativa del objeto '''
		return self.posicion + " - " + self.jugador.nombre

########################################################################

class AlineacionEquipo(models.Model):
	''' Representa la alineación de un equipo en un partido '''
	equipo = models.ForeignKey(Equipo)
	jugadores = models.ManyToManyField(JugadorPartido, null = True, blank = True)

	def borrarAlineacion(self):
		''' Elimina la alineacion actual '''
		for jugador in self.jugadores.all():
			jugador.delete()

	def setAlineacion(self, portero, defensas, centrocampistas, delanteros, suplentes):
		''' Establece una alineacion de jugadores a partir de los ids '''
		self.borrarAlineacion()

		jugador = self.equipo.jugador_set.get(id = portero)
		p = JugadorPartido(jugador = jugador, posicion = 'PO')
		p.save()
		self.jugadores.add(p)

		for id_jugador in defensas:
			jugador = self.equipo.jugador_set.get(id = id_jugador)
			j = JugadorPartido(jugador = jugador, posicion = 'DF')
			j.save()
			self.jugadores.add(j)

		for id_jugador in centrocampistas:
			jugador = self.equipo.jugador_set.get(id = id_jugador)
			j = JugadorPartido(jugador = jugador, posicion = 'CC')
			j.save()
			self.jugadores.add(j)

		for id_jugador in delanteros:
			jugador = self.equipo.jugador_set.get(id = id_jugador)
			j = JugadorPartido(jugador = jugador, posicion = 'DL')
			j.save()
			self.jugadores.add(j)

		for id_jugador in suplentes:
			jugador = self.equipo.jugador_set.get(id = id_jugador)
			j = JugadorPartido(jugador = jugador, posicion = 'BA')
			j.save()
			self.jugadores.add(j)

	def getTitulares(self):
		''' Devuelve los jugadores titulares '''
		datos = self.getDatosTitulares()
		lista = []
		for dato in datos:
			jugador = dato.jugador
			lista.append(jugador)
		return lista

	def getSuplentes(self):
		''' Devuelve los jugadores suplentes '''
		datos = self.getDatosSuplentes()
		lista = []
		for dato in datos:
			jugador = dato.jugador
			lista.append(jugador)
		return lista

	def getDelanteros(self):
		''' Devuelve los delanteros del equipo '''
		lista = self.jugadores.filter(posicion = 'DL')
		if len(lista) > 0:
			return lista
		return None

	def getCentrocampistas(self):
		''' Devuelve los centrocampistas del equipo '''
		lista = self.jugadores.filter(posicion = 'CC')
		if len(lista) > 0:
			return lista
		return None

	def getDefensas(self):
		''' Devuelve los defensas del equipo '''
		lista = self.jugadores.filter(posicion = 'DF')
		if len(lista) > 0:
			return lista
		return None

	def getPortero(self):
		''' Devuelve al portero del equipo '''
		lista = self.jugadores.filter(posicion = 'PO')
		if len(lista) > 0:
			return lista[0]
		return None

	def getSuplentes(self):
		''' Devuelve los suplentes del equipo '''
		lista = self.jugadores.filter(posicion = 'BA')
		if len(lista) > 0:
			return lista
		return None

	def getDatosTitulares(self):
		''' Devuelve los datos de los titulares '''
		return self.jugadores.all().exclude(posicion = 'BA')

	def getDatosSuplentes(self):
		''' Devuelve los datos de los suplentes '''
		return self.jugadores.filter(posicion = 'BA')

	def setAleatoria(self):
		jugadores_equipo = self.equipo.jugador_set.all()

		for i in range(16):
			posiciones = ['PO', 'DF', 'DF', 'DF', 'DF', 'CC', 'CC', 'CC', 'CC', 'DL', 'DL', 'BA', 'BA', 'BA', 'BA', 'BA']
			jugador = JugadorPartido(jugador = jugadores_equipo[i], posicion = posiciones[i])
			jugador.save()
			self.jugadores.add(jugador)

	def estaPreparada(self):
		return len(self.jugadores.all()) > 0

	def getValorAtaque(self):
		valor = 0
		titulares = self.getDatosTitulares()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			ataque = titulares[i].ataque

			if(posicion == "DF"):
				valor += (int)(ataque * 0.25)
			elif(posicion == "CC"):
				valor += (int)(ataque * 0.75)
			elif(posicion == "DL"):
				valor += ataque

		return valor / (num_jugadores_campo - 1)

	def getValorDefensa(self):
		valor = 0
		titulares = self.getDatosTitulares()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			defensa = titulares[i].defensa

			if(posicion == "DF"):
				valor += defensa
			elif(posicion == "CC"):
				valor += (int)(defensa * 0.75)
			elif(posicion == "DL"):
				valor += (int)(defensa * 0.25)

		return valor / (num_jugadores_campo - 1)

	def getValorPases(self):
		valor = 0
		titulares = self.getDatosTitulares()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			pases = titulares[i].pases
			if(posicion == "DF"):
				valor += (int)(pases * 0.75)
			elif(posicion == "CC"):
				valor += pases
			elif(posicion == "DL"):
				valor += (int)(pases * 0.75)

		return valor / (num_jugadores_campo - 1)

	def getValorVelocidad(self):
		valor = 0
		titulares = self.getDatosTitulares()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			velocidad = titulares[i].velocidad
			if(posicion == "DF"):
				valor += (int)(velocidad * 0.75)
			elif(posicion == "CC"):
				valor += velocidad
			elif(posicion == "DL"):
				valor += (int)(velocidad * 0.75)

		return valor / (num_jugadores_campo - 1)

	def getValorAnotacion(self):
		valor = 0
		titulares = self.getDatosTitulares()
		num_jugadores_campo = len(titulares)
		for i in range(0, num_jugadores_campo):
			posicion = titulares[i].posicion
			anotacion = titulares[i].anotacion
			if(posicion == "DF"):
				valor += (int)(anotacion * 0.5)
			elif(posicion == "CC"):
				valor += (int)(anotacion * 0.75)
			elif(posicion == "DL"):
				valor += anotacion

		return valor / (num_jugadores_campo - 1)

	def getValorPortero(self):
		valor = 0
		i = 0
		titulares = self.getDatosTitulares()
		num_jugadores_campo = len(titulares)
		while (i < num_jugadores_campo) and (valor == 0):
			posicion = titulares[i].posicion

			if(posicion == "PO"):
				valor = titulares[i].portero

			i += 1

		return valor

########################################################################

# Partido
class Partido(models.Model):
	''' Representa un partido en el sistema '''
	#hora_inicio = models.TimeField("Hora de inicio")
	jornada = models.ForeignKey(Jornada)
	equipo_local = models.ForeignKey(Equipo, related_name = "Local")
	equipo_visitante = models.ForeignKey(Equipo, related_name = "Visitante")

	alineacion_local = models.ForeignKey(AlineacionEquipo, related_name = "AlineacionLocal")
	alineacion_visitante = models.ForeignKey(AlineacionEquipo, related_name = "AlineacionVisitante")

	goles_local = models.IntegerField(null = True, blank = True)
	goles_visitante = models.IntegerField(null = True, blank = True)

	jugado = models.BooleanField()

	def __init__(self, *args, **kwargs):
		super(Partido, self).__init__(*args, **kwargs)
		if not self.alineacion_local_id:
			self.alineacion_local = AlineacionEquipo(equipo = self.equipo_local)
			self.alineacion_visitante = AlineacionEquipo(equipo = self.equipo_visitante)
			self.alineacion_local.save()
			self.alineacion_visitante.save()
			self.alineacion_local_id = self.alineacion_local.id
			self.alineacion_visitante_id = self.alineacion_visitante.id

	def finalizado(self):
		''' Indica si un partido ya ha acabado '''
		return self.jugado

	def jugar(self):
		''' Juega el partido '''
		num_goles = [0, 0]

		if not self.alineacion_local.estaPreparada():
			print "preparing"
			self.alineacion_local.setAleatoria()

		if not self.alineacion_visitante.estaPreparada():
			self.alineacion_visitante.setAleatoria()

		# Obtener alineaciones de los 2 equipos
		alineacion_local = self.alineacion_local
		alineacion_visitante = self.alineacion_visitante

		# Obtener jugadores titulares y suplentes de los 2 equipos
		titulares_local = self.alineacion_local.getDatosTitulares()
		suplentes_local = self.alineacion_local.getDatosSuplentes()
		titulares_visitante = self.alineacion_visitante.getDatosTitulares()
		suplentes_visitante = self.alineacion_visitante.getDatosSuplentes()

		alineacion = [alineacion_local, alineacion_visitante]

		num_parte = 1 # Parte de partido que se está jugando

		# Inicializar variables para el partido
		# --------------------------------------
		ataque = [alineacion[0].getValorAtaque(), alineacion[1].getValorAtaque()]
		defensa = [alineacion[0].getValorDefensa(), alineacion[1].getValorDefensa()]
		pases = [alineacion[0].getValorPases(), alineacion[1].getValorPases()]
		velocidad = [alineacion[0].getValorVelocidad(), alineacion[1].getValorVelocidad()]
		anotacion = [alineacion[0].getValorAnotacion(), alineacion[1].getValorAnotacion()]
		portero = [alineacion[0].getValorPortero(), alineacion[1].getValorPortero()]
		# --------------------------------------

		los_gatos_nos_dominaran = True
		if not los_gatos_nos_dominaran:
			print "-------------------------------------------"
			print alineacion[0].equipo.nombre
			print "Ataque: " + str(alineacion[0].getValorAtaque())
			print "Defensa: " + str(alineacion[0].getValorDefensa())
			print "Pases: " + str(alineacion[0].getValorPases())
			print "Velocidad: " + str(alineacion[0].getValorVelocidad())
			print "Anotacion: " + str(alineacion[0].getValorAnotacion())
			print "Portero: " + str(alineacion[0].getValorPortero())
			print "-------------------------------------------"
			print alineacion[1].equipo.nombre
			print "Ataque: " + str(alineacion[1].getValorAtaque())
			print "Defensa: " + str(alineacion[1].getValorDefensa())
			print "Pases: " + str(alineacion[1].getValorPases())
			print "Velocidad: " + str(alineacion[1].getValorVelocidad())
			print "Anotacion: " + str(alineacion[1].getValorAnotacion())
			print "Portero: " + str(alineacion[1].getValorPortero())
			print "-------------------------------------------"

		# Continuar jugando mientras no se hayan acabado las 2 partes del partido
		while(num_parte <= 2):
			# Establecer equipo que comienza a jugar la parte
			if(num_parte == 1):
				# Sortear equipo que comienza
				equipo_comienza = randint(0, 1)
				id_equipo_atacante = equipo_comienza
				segundos_jugados = 0
			else:
				if(equipo_comienza == 0): id_equipo_atacante = 1
				else: id_equipo_atacante = 0
				segundos_jugados = 45 * 60

			# Iniciar variables
			seg_restantes = 45 * 60
			tiempo_descuento = False

			# Continuar jugando mientras no se haya acabado todo el tiempo de la parte actual
			while(seg_restantes > 0):
				# Establecer id del defensor
				if(id_equipo_atacante == 0): id_equipo_defensor = 1
				else: id_equipo_defensor = 0

				# Crear jugada
				num_acciones = (randint(2, 20) + randint(2, 20) + randint(2, 20)) / 3
				seg_accion = 2 + (int)((100.0 - velocidad[id_equipo_atacante]) / 10) + randint(0, 2)

				#print "\t" + "num_acciones: " + str(num_acciones) + " (" + str(seg_accion) + " seg / accion)"
				formula = (1.0 * ataque[id_equipo_atacante]) / pases[id_equipo_atacante]
				prob_regate = probabilidadExito(formula)
				#print "Prob Pase/Regate (" + str(prob_regate) + "%) "
				accion = 1
				while (accion <= num_acciones) and (id_equipo_defensor != id_equipo_atacante):
					#print "\t" + str(accion) + ".- "

					# Realizar una de las acciones de la jugada completa
					if(accion != num_acciones):
						# Calcular probabilidad de que la acción sea un pase o un regate
						# Regate
						if(randint(1, 100) <= prob_regate):
							formula = (1.0 * ataque[id_equipo_atacante] / defensa[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Regate (" + str(prob_exito) + "%) "
							if(randint(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor
						# Pase
						else:
							formula = (pases[id_equipo_atacante] * 2.0) / (defensa[id_equipo_defensor] + velocidad[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Pase (" + str(prob_exito) + "%) "
							if(randint(1, 100) > prob_exito):
								id_equipo_atacante = id_equipo_defensor

					# Disparo a puerta
					else:
						# Calcular probabilidad de que el disparo vaya a portería (95% de la anotación)
						prob_exito = anotacion[id_equipo_atacante] * 0.95

						# Si el balón va a portería
						if(randint(1, 100) <= prob_exito):
							formula = (1.0 * anotacion[id_equipo_atacante] / portero[id_equipo_defensor])
							prob_exito = probabilidadExito(formula)
							#print "Disparo a puerta (" + str(prob_exito) + "%) "
							if(randint(1, 100) > prob_exito):
								texto = "Disparo parado"
								#print texto
								if id_equipo_atacante == 0:
									equipo_suceso = self.equipo_local
								else:
									equipo_suceso = self.equipo_visitante
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)

								id_equipo_atacante = id_equipo_defensor
							# Marcar gol
							else:
								num_goles[id_equipo_atacante] += 1

								texto = "Gol"
								#print texto
								if id_equipo_atacante == 0:
									equipo_suceso = self.equipo_local
								else:
									equipo_suceso = self.equipo_visitante
								suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
								self.suceso_set.add(suceso)

								# Ahora sacará el equipo contrario
								id_equipo_atacante = id_equipo_defensor

								# Tiempo perdido en la celebración del gol
								seg_restantes -= 30
								segundos_jugados += 30
						# Fuera
						else:
							texto = "Disparo fuera"
							#print texto
							if id_equipo_atacante == 0:
								equipo_suceso = self.equipo_local
							else:
								equipo_suceso = self.equipo_visitante
							suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
							self.suceso_set.add(suceso)

					seg_restantes -= seg_accion
					segundos_jugados += seg_accion
					accion += 1

				# Minutos de descuento
				if(seg_restantes <= 0):
					if(tiempo_descuento == False):
						tiempo_descuento = True
						min_descuento = randint(1, 5)
						seg_restantes += ((min_descuento * 60) + randint(0, 30))

						texto = "TIEMPO DESCUENTO (" + str(min_descuento) + " minutos)"
						#print texto
						if id_equipo_atacante == 0:
							equipo_suceso = self.equipo_local
						else:
							equipo_suceso = self.equipo_visitante
						suceso = Suceso(segundo_partido = segundos_jugados - (segundos_jugados % 60), tipo = texto, equipo = equipo_suceso)
						self.suceso_set.add(suceso)
					else:
						texto = "FIN DE LA " + str(num_parte) + "ª PARTE"
						#print texto
						if id_equipo_atacante == 0:
							equipo_suceso = self.equipo_local
						else:
							equipo_suceso = self.equipo_visitante
						suceso = Suceso(segundo_partido = segundos_jugados, tipo = texto, equipo = equipo_suceso)
						self.suceso_set.add(suceso)

			num_parte += 1

		self.goles_local = num_goles[0]
		self.goles_visitante = num_goles[1]
		self.jugado = True

	def __unicode__(self):
		''' Devuelve una cadena de texto que representa la clase '''
		return "Partido de %s contra %s en jornada %d de liga %d" % (self.equipo_local.nombre, self.equipo_visitante.nombre, self.jornada.numero, self.jornada.liga.id)

########################################################################

class Suceso(models.Model):
	''' Representa un suceso de un partido (gol, falta, etc) '''
	segundo_partido = models.IntegerField(null = True, blank = True)
	tipo = models.CharField(max_length = 50)

	equipo = models.ForeignKey(Equipo)
	partido = models.ForeignKey(Partido)

	def getMinuto(self):
		return self.segundo_partido / 60

	def getSegundo(self):
		return self.segundo_partido % 60

########################################################################