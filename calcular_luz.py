#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from subprocess import call
from datetime import datetime
import requests
import json
import statistics

# ------------------ Variables globales --------------------- #

TOKEN = "" #Token de acceso
ID_PENINSULA = 8741 #Para filtrar por los precios de la Peninusula
URL = 'https://api.esios.ree.es/indicators/1001'
CABECERAS = {'Accept':'application/json; application/vnd.esios-api-v2+json','Content-Type':'application/json','Host':'api.esios.ree.es','Authorization':'Token token=\"' + TOKEN + '\"'}
DIRECTORIO_LOGS = '' #ruta de guardado de logs con los precios max/min/med del dia

# ------------------------ Metodos -------------------------- #

def obtener_datos():

    response = requests.get(URL, headers=CABECERAS)

    if response.status_code == 200:  #conexion correcta
        datos_json = json.loads(response.text) #almacenamos respuesta en formato JSON
        return datos_json
    
    return datos_json #si tenemos error salimos directamente


def calcular_precios(datos_json):
    
        #Para filtrar por valores, y solo aquellos que sean de la Peninsula
        valores = datos_json['indicator']['values']
        valores_peninsula = [x for x in valores if x['geo_id'] == ID_PENINSULA]

        #Recogiendo precios
        precios = [x['value'] for x in valores_peninsula]

        #Convirtiendo a precios en kWh
        i = 0
        for x in precios:
            precios[i] = round(float(precios[i])*0.001, 4) #para que de precios en kWh
            i = i+1

        #Guardando los precios (minimo, maximo, media) en un logfile
        registro = 'echo \"' + '{\"Date: \"' + str(datetime.today().strftime('%d-%m-%Y')) + ', \"Maximo\": ' + str(max(precios)) + ', \"Minimo\": ' + str(min(precios)) + ', \"Media\": ' + str(round(statistics.mean(precios), 4)) + '}\"' + ' >> ' + DIRECTORIO_LOGS + '/precios.txt'
        call(registro, shell=True)

        return precios


def asignar_horarios(precios):
    
    desv_tipica = round(statistics.stdev(precios), 4)
    horario = []

    for x in precios:
        if x <= desv_tipica:
            horario.append(True)
        
        else: horario.append(False)
    
    # Mantener servidor encendido si previamente estaba encendido 
    # y a la hora siguiente se encenderá también, limitando desgaste
    # de los componentes

    i = 1
    for x in range(1, len(horario)-2):
        if x == 0:
            if horario[i-1] == 1 and horario[i+1] == 1:
                horario[i] = 1
    
    return horario


def crear_tareas(horario):
    
    i = 0
    for x in horario:
        if x:
            comando = 'echo \"sh encender.sh\" | at ' + str(i) + ':00 >/dev/null 2>&1 &'
            call(comando, shell=True)
        
        else:
            comando = 'echo \"sh apagar.sh\" | at ' + str(i) + ':00 >/dev/null 2>&1 &'
            call(comando, shell=True)
        
        i = i+1 #siguiente hora


def main():

    datos_json = obtener_datos() #conectando con api

    if len(datos_json) == 0: #error al procesar la peticion, json no valido (vacio)
        sys.exit(-1) 
        
    precios = calcular_precios(datos_json) #filtrado de precios y valores en kWh
    horario = asignar_horarios(precios) #segun el precio de cada hora, encender/apagar servidor
    crear_tareas(horario) #creacion de tareas de encendido/apagado para cada hora
    return 0


# ------------------- Codigo ejecutado ------------------ #

main()