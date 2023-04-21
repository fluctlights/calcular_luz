#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from subprocess import call
from datetime import datetime
import requests
import json
import statistics
import subprocess

# ------------------ Variables globales --------------------- #

TOKEN = "" #Token de acceso
ID_PENINSULA = 8741 #Para filtrar por los precios de la Peninusula
URL = 'https://api.esios.ree.es/indicators/1001'
CABECERAS = {'Accept':'application/json; application/vnd.esios-api-v1+json','Host':'api.esios.ree.es','Content-Type':'application/json','x-api-key':'\"'+TOKEN+'\"'}
DIRECTORIO_LOGS = '/home/pi/api_ree_logs/' #ruta de guardado de logs con los precios max/min/med del dia


# ------------------------ Metodos -------------------------- #

def obtener_datos():
    try :
        response = requests.get(URL, headers=CABECERAS)
        datos_json = {}
        if response.status_code == 200:  #conexion correcta
            datos_json = json.loads(response.text) #almacenamos respuesta en formato JSON
            return datos_json
    except Exception as e:
        print(str(e))
        return datos_json #si tenemos error salimos directamente


def calcular_precios(datos):
    
        #Para filtrar por valores, y solo aquellos que sean de la Peninsula
        valores = datos['indicator']['values']
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
    
    horario = []

    for x in precios:
        if x <= 0.10:
            horario.append(True)
        
        else: horario.append(False)
    
    # Mantener servidor encendido si previamente estaba encendido 
    # y a la hora siguiente se encenderá también, limitando desgaste
    # de los componentes

    for x in range(0, len(horario)):
        
        if (horario[x] == False):
            
            if x is 0:
                if (horario[x+1] == True) and (horario[x+2] == True):
                    subset = [precios[x+1], precios[x], precios[x+2]]
                    if round(statistics.mean(subset), 4) <= 0.1150:
                        horario[x] = True
                        
            elif x is (len(horario)-1):
                if (horario[x-1] == True) and (horario[x-2] == True):
                    subset = [precios[x-1], precios[x], precios[x-2]]
                    if round(statistics.mean(subset), 4) <= 0.1150:
                        horario[x] = True
                        
            else:
                if (horario[x-1] == True) and (horario[x+1] == True):
                    subset = [precios[x-1], precios[x], precios[x+1]]
                    if round(statistics.mean(subset), 4) <= 0.1150:
                        horario[x] = True
    
    return horario


def crear_tareas(horario):
    
    for x in range (0, len(horario)):
        if horario[x]:
            #comando = 'echo \"sudo /bin/bash encender.sh\" | at ' + str(x) + ':02 >/dev/null 2>&1 &'
            comando = 'echo \"sudo /bin/bash encender.sh\" | at ' + str(x) + ':02'
            subprocess.Popen(comando, shell=True)
        
        else:
            #comando = 'echo \"/bin/bash apagar.sh\" | at ' + str(x) + ':02 >/dev/null 2>&1 &'
            comando = 'echo \"/bin/bash apagar.sh\" | at ' + str(x) + ':02'
            subprocess.Popen(comando, shell=True)
        
def main():

    datos = obtener_datos() #conectando con api

    if len(datos) == 0: #error al procesar la peticion, json no valido (vacio)
        print("err")
        sys.exit(-1) 
        
    precios = calcular_precios(datos) #precios y valores en kWh
    horario = asignar_horarios(precios) #segun el precio de cada hora, encender/apagar servidor
    crear_tareas(horario) #creacion de tareas de encendido/apagado para cada hora
    return 0


# ------------------- ToDo ------------------ #

main()
