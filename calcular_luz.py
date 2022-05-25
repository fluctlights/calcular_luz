#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
#from webbrowser import get
from subprocess import call
import requests
import json
import statistics

TOKEN = "b8cdeb86a9e01c367f4a2fcf5b76580088eab4677ce4cee21d0523489d896b4a" #Token de acceso
ID_PENINSULA = 8741 #Para filtrar por los precios de la Peninusula
URL = 'https://api.esios.ree.es/indicators/1001'
CABECERAS = {'Accept':'application/json; application/vnd.esios-api-v2+json','Content-Type':'application/json','Host':'api.esios.ree.es','Authorization':'Token token=\"TOKEN\"'}

def calcular_luz(datos_json):
    
        #Para filtrar por valores, y solo aquellos que sean de la Peninsula
        valores = datos_json['indicator']['values']
        valores_peninsula = [x for x in valores if x['geo_id'] == ID_PENINSULA]

        #Recogiendo precios
        precios = [x['value'] for x in valores_peninsula]
        return precios

def obtener_precios(datos_json, valor): #cada dia, este hilo se activara para leer los valores nuevos

    response = requests.get(URL, headers=CABECERAS)

    if response.status_code == 200:  #conexion correcta
        datos_json = json.loads(response.text) #almacenamos respuesta en formato JSON
        return datos_json
    
    else: return datos_json

def precios_float(precios):

    #transformando a array de valores numericos
    valores_numericos = []
    i = 0

    for x in precios:
        valores_numericos[i] = float(x)
        i = i+1

    return valores_numericos

def asignar_horarios(valores_numericos):
    
    desv_tipica = round(statistics.stdev(valores_numericos),3)
    i = 0
    horario = []

    for x in valores_numericos:
        if x <= desv_tipica:
            horario[i] = True
        else: horario[i] = False
        i = i+1
    
    return horario

def arreglar_horarios(horario):
    i = 1
    for x in range(1, horario-2):
        if x == 0:
            if horario[i-1] == 1 and horario[i+1] == 1:
                horario[i] = 1
    
    return horario


def ejecutar_comandos(horario):
    i = 0
    comando = ''
    for x in horario:
        if x:
            comando = 'echo \"sh encender.sh\" | at ' + i + ':00'
            call(comando, shell=True)
        
        else:
            comando = 'echo \"sh apagar.sh\" | at ' + i + ':00'
            call(comando, shell=True)

# ------------------- Main ------------------ #

datos_json = obtener_precios()

if len(datos_json) == 0: #error al procesar la peticion, json no valido (vacio)
    sys.exit(-1) 
    
precios = calcular_luz(datos_json)
valores_numericos = precios_float(precios)

#obteniendo minimo, maximo y media
precio_minimo = min(valores_numericos)
precio_maximo = max(valores_numericos)
precio_medio = round(statistics.mean(valores_numericos),3)

horario = asignar_horarios(valores_numericos, precio_medio)
horario = arreglar_horarios(horario)

ejecutar_comandos(horario)