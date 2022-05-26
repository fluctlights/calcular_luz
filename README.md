# calcular_luz.py

------------------------------------------------------------------------------------
 Herramienta para encender/apagar un servidor según el precio de la luz de cada día
------------------------------------------------------------------------------------

*Este programa todavía está en desarrollo*

La idea de este programa es, mediante el uso de Crontab, obtener los precios de la luz
(en horas) diariamente. Nos conectamos con el token que nos proporciona REE y mediante
la API ESIOS hacemos una consulta para recoger los valores de los precios para la 
Península. Según los precios dados, el programa creará tareas para encender/apagar el
servidor (si estaba ya encendido sigue funcionando, no afecta) Para esto es necesario 
poner en la variable global TOKEN el valor del token concreto.

Para el guardado de precios max/min/med diarios, es necesario introducir el directorio
concreto donde queremos guardarlos. Esto se hace poniendo en la variable global
DIRECTORIO_LOGS el directorio deseado. Los logs se guardaran en un archivo llamado
precios.txt
