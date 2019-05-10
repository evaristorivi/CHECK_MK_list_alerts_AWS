#!/usr/bin/python
# -*- coding: utf-8 -*-

# CHECK_MK_list_alerts_v1 AWS
# Evaristo R. Rivieccio Vega - Cloud, Middleware y Sistemas - L1
# evaristorivieccio@gmail.com

import boto3
import sys
import datetime
from dateutil import tz

#Estados de salida para Check_MK
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

#Devuelve la hora actual(UTC)
def hora_actual_utc():
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()
    central=datetime.datetime.now()
    central = central.replace(tzinfo=from_zone)
    utc = central.astimezone(to_zone)
    actual_time = utc.strftime('%s')
    actual_time=int(actual_time)
    return actual_time

#Lista las alarmas de CloudWacht que pueden ser: #StateValue='OK'|'ALARM'|'INSUFFICIENT_DATA'
def list_alarms():
    alertas=False
    # Crea cliente CloudWatch
    cloudwatch = boto3.client('cloudwatch')
    contadoralarm=0
    # Lista alarmas con paginator
    paginator = cloudwatch.get_paginator('describe_alarms')
    
    tipo=''
    fullalarms=[]
    
    #Saca Datos
    for response in paginator.paginate():
        alarmstatus = (response['MetricAlarms'])
        for item in alarmstatus:
            #Hora de última modificación del estado de la alrma
            alarm_time = int(item['StateUpdatedTimestamp'].strftime('%s'))
            #Diferencia de la hora actual - la hora de la última modificación del estado de la alarma
            diff = hora_actual_utc() - alarm_time
            #print diff
            #Guardamos en una lista todas las alarmas.
            fullalarms.append((item['AlarmArn'],item['StateValue']))
            #Si la diferencia es mayor que: #30 minutos==1800
            if diff > 1800:
                alertas=True
                contadoralarm = contadoralarm+1
                if item['StateValue']=='ALARM':
                    tipo='ALARM'
                elif item['StateValue']=='INSUFFICIENT_DATA':
                    tipo='INSUFFICIENT_DATA'
        print "\n"
        if alertas is True and tipo=='INSUFFICIENT_DATA':
            #pprint(alarmstatus)
            message="Hay " + str(contadoralarm) + " alarma/s que requieren atención.\n" + str(fullalarms)
            end(1, message)
        elif alertas is True and tipo=='ALARM':
            message="Hay " + str(contadoralarm) + " alarma/s que requieren atención. \n" + str(fullalarms)
            end(2, message)
        else:
            message="No hay problemas con las alertas \n" + str(fullalarms)
            end(0, message)
            
list_alarms()
