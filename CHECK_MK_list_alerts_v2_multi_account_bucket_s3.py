#!/usr/bin/python
# -*- coding: utf-8 -*-

# CHECK_MK_list_alerts_v2_multi_account_bucket_s3 AWS
# Evaristo R. Rivieccio Vega - Cloud, Middleware y Sistemas - L1
# evaristorivieccio@gmail.com

import boto3
import sys
import datetime
from dateutil import tz
import pickle


# CONFIG
######################################################
######################################################

# CONFIG de S3
BUCKET = '<nombre del bucket, no el arn, sino el nombre>'
FICHERO_DATOS = '<nombre_fichero.pkl que está en el bucket s3>'

######################################################
######################################################


# Carga objetos
def load_obj(name):
    with open('/tmp/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


# Estados de salida para Check_MK
def end(state, message):
    """Return the error"""        
    if state is 0:
        print("OK: " + str(message) + "|state=" + str(state))
        sys.exit(state)
    elif state is 1:
        print("WARNING: " + str(message) + "|state=" + str(state))
        sys.exit(state)
    else:
        print("CRITICAL: " + str(message) + "|state=" + str(state))
        sys.exit(state)

# Devuelve la hora actual(UTC)
def hora_actual_utc():
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()
    central=datetime.datetime.now()
    central = central.replace(tzinfo=from_zone)
    utc = central.astimezone(to_zone)
    actual_time = utc.strftime('%s')
    actual_time=int(actual_time)
    return actual_time

# Lista las alarmas de CloudWacht que pueden ser: #StateValue='OK'|'ALARM'|'INSUFFICIENT_DATA'
def list_alarms():
    alertas=False
    # Crea cliente CloudWatch
    contadoralarm=0
    contadorins=0
    # Lista alarmas con paginator
    
    tipo=''
    alarmalarms=["ALARM \n"]
    insalarms=["INSUFFICIENT_DATA \n"]
    # Saca Datos
    # Obtenemos los datos del s3
    s3_client = boto3.client('s3')
    s3_client.download_file(BUCKET, FICHERO_DATOS, '/tmp/datadowload.pkl')
    data=load_obj('datadowload')
    for a in data:
        for item in a:
 
            # Hora de última modificación del estado de la alrma
            alarm_time = int(item['StateUpdatedTimestamp'].strftime('%s'))
            # Diferencia de la hora actual - la hora de la última modificación del estado de la alarma
            diff = hora_actual_utc() - alarm_time
            #print diff
            # Guardamos en una lista todas las alarmas.
            # Si la diferencia es mayor que: #30 minutos==1800
            
            if diff > 1800:
                alertas=True
                if item['StateValue']=='ALARM':
                    contadoralarm = contadoralarm+1
                    # Array de todas las alarmas con estado ALARM
                    alarmalarms.append((item['AlarmArn'],item['StateValue']))
                    alarmalarms.append("\n")
                    tipo='ALARM'
                elif item['StateValue']=='INSUFFICIENT_DATA':
                    contadorins = contadorins+1
                    tipo='INSUFFICIENT_DATA'
                    # Array de todas las alarmas con estado INSUFFICIENT_DATA
                    insalarms.append((item['AlarmArn'],item['StateValue']))
                    insalarms.append("\n")
            # Todas las alarmas que no son OK
            fullalarms=[insalarms,alarmalarms]


    if alertas is True and tipo=='INSUFFICIENT_DATA':
        #pprint(alarmstatus)
        message="Hay " + str(contadorins) + " alerta/s que llevan más de 30 minutos con estado INSUFFICIENT_DATA \n" + str(fullalarms)
        end(1, message)
    elif alertas is True and tipo=='ALARM':
        print tipo
        message="Hay " + str(contadoralarm) + " alerta/s que llevan más de 30 minutos con estado ALARM \n" + str(fullalarms)
        end(2, message)
    else:
        print tipo
        message="No hay problemas con las alertas \n"
        end(0, message)
                

list_alarms()
