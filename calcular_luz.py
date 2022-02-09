import requests
import json
import statistics

#Creando el objeto JSON (cabeceras), que requiere un token personal y la URL que referencia la tarifa
TOKEN = "b8cdeb86a9e01c367f4a2fcf5b76580088eab4677ce4cee21d0523489d896b4a" #Introducir el token personal que te da REE
url = 'https://esios.ree.es/indicators/10229' #pagina que referencia a la PVPC 2.0A 
headers = {'Accept':'application/json; application/vnd.esios-api-v2+json','Content-Type':'application/json','Host':'api.esios.ree.es','Authorization':'Token token=' + TOKEN}
#Obtener respuesta de la API tras meter la cabecera. y la URL que tiene la tarifa
response = requests.get(url, headers=headers)

#Si la respuesta es valida, continuamos
if response.status_code == 200:

    json_data = json.loads(response.text)
    valores = json_data['indicator']['values']
    #print(response.json())

    precios = [x['value'] for x in valores]
    
    hora = 0
    for precio in precios:
        print("%s horas - %s €" %(str(hora).zfill(2), str(round(precio/1000, 4))))
        hora += 1
    
    valor_min = min(precios)
    valor_max = max(precios)
    valor_med = round(statistics.mean(precios),2)
    
    print("Precio mínimo: %s" % str(valor_min/1000))
    print("Precio máximo: %s" % str(valor_max/1000))
    print("Precio medio: %s" % str(valor_med/1000))

    '''
    json_data = json.loads(response.text) #decodificamos la respuesta de la API
    valores = json_data['indicator']['values'] #Formateamos la array de arriba, donde tenemos [ID, valor]
    precios = [x['value'] for x in valores] #crear array de 24 filas, cada hora, un precio.
    buena_hora = [False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False] #boolean que recoge si el precio es bueno o no, segun la lista precios
    puntero = 0 #para rellenar las horas
    dif = 0 #si la diferencia es pequeña entre horas contiguas, entonces tambien entrara la hora conflictiva en las horas validas
    valor_med = round(statistics.fmean(precios),2) #media del precio de electricidad del dia 
    valor_valido_sup = valor_med + 0.005  #limite que marco yo mismo de lo que es razonabl
    intervalo = [] #para generar los intervalos validos 
    encendido_apagado = [] #para marcar los horarios concretos en una lista

    for precio in precios:
        if precio < valor_valido_sup:
            buena_hora[puntero] = True
        else:
            if puntero > 0:
                if buena_hora[puntero - 1]: #si la anterior hora entraba en mi intervalo, la resta se hara de una forma
                    dif = abs(precio[puntero] - precio[puntero-1]) #diferencia entre hora anterior y actual
                    if dif < 0.00105: #para no apagar y encender por pequeña diferencia entre horas consecutivas, marco un limite mayor
                        buena_hora[puntero] = True #si entro, es una hora valida tambien
                    else:
                        buena_hora[puntero] = False #hora no valida, el ordenador se apagaría
                else: #si no, entonces se hara al reves
                    dif = abs(precio[puntero-1] - precio[puntero])
                    if dif < 0.00105:
                        buena_hora[puntero] = True
                    else:
                        buena_hora[puntero] = False
            else:
                buena_hora[puntero] = False #dado que es la primera hora, tampoco nos vamos a morir por tenerlo apagado un poco mas
        puntero += 1
    
    puntero = 0 #vamos a usar otra vez esta variable, para recorrer lista buena_hora, asi que la reinicializamos
    
    for hora in buena_hora:
        if not hora:
            if puntero > 0:
                if hora[puntero-1] == True & hora[puntero+1] == True: #si las horas contiguas son validas, hacemos tambien valida la del medio
                    hora[puntero] = True
        else:
            if puntero > 0:
                if hora[puntero-1] == False & hora[puntero+1] == False: #si las horas contiguas son malas, hacemos tambien mala la del medio
                    hora[puntero] = False
        puntero += 1

    puntero = 0 #otra vez reutilizamos
    
    while(True):
        valor = 0
        if puntero == 24:
            break
        else:
            if buena_hora[puntero]:
                valor = puntero
                while(buena_hora[puntero]):
                    puntero += 1
                intervalo.append((valor,puntero-1))
            else:
                puntero += 1

    puntero = 0
    
    for interv in intervalo:
        encendido_apagado.append(interv[puntero][0])
        encendido_apagado.append(interv[puntero][1])
        puntero+=1

    ruta = "/var/spool/cron/crontabs"

    '''