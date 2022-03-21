# Dieses Script überprüft welche Zelle die meiste Spannung besitzt und welche Spannung diese hat
# Danach wird die maximale Spannung des Victron Systems eingestellt.
# Dies hilft mit einer höhreren Spannung zu laden und dann wenn der Akku nahezuvoll ist
# Die Spannung zu reduzieren um den Akku nicht zu überladen

import time
import paho.mqtt.client as mqtt
import logging
import json

cerboserial = "123456789"    # Ist auch gleich VRM Portal ID
broker_address = "192.168.1.xxx"

#  Einstellen der Limits (Über Maxvoltcell1 wird Stufe 2 eingesetzt, über 2 dann 3 usw.)

MaxVoltStufe1 = 55.0
MaxVoltStufe2 = 54.8
MaxVoltStufe3 = 54.4
MaxVoltStufe4 = 54.2
MaxVoltStufe5 = 54.0

MaxVoltCell1 = 3.4
MaxVoltCell2 = 3.45
MaxVoltCell3 = 3.5
MaxVoltCell4 = 3.6

# Pfade

MaxCellVoltagePath = "/battery/512/System/MaxCellVoltage"
MaxChargeVoltagePath = "/settings/0/Settings/SystemSetup/MaxChargeVoltage"

# Variblen setzen
verbunden = 0
durchlauf = 0
maxcellvoltage = 3.0

logging.basicConfig(filename='Error.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

def on_disconnect(client, userdata, rc):
    global verbunden
    print("Client Got Disconnected")
    if rc != 0:
        print('Unexpected MQTT disconnection. Will auto-reconnect')

    else:
        print('rc value:' + str(rc))

    try:
        print("Trying to Reconnect")
        client.connect(broker_address)
        verbunden = 1
    except Exception as e:
        logging.exception("Fehler beim reconnecten mit Broker")
        print("Error in Retrying to Connect with Broker")
        verbunden = 0
        print(e)

def on_connect(client, userdata, flags, rc):
        global verbunden
        if rc == 0:
            print("Connected to MQTT Broker!")
            verbunden = 1
            client.subscribe("N/" + cerboserial + MaxCellVoltagePath)
        else:
            print("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    try:

        global maxcellvoltage
        if msg.topic == "N/" + cerboserial + MaxCellVoltagePath:   # MaxCellVoltage auslesen
            if msg.payload != '{"value": null}' and msg.payload != b'{"value": null}':
                maxcellvoltage = json.loads(msg.payload)
                maxcellvoltage = round(float(maxcellvoltage['value']), 2)
            else:
                print("MaxCellVoltage war Null und wurde ignoriert")

    except Exception as e:
        logging.exception("Programm MVMC ist abgestürzt. (on message Funkion)")
        print(e)
        print("Im MVMC Programm ist etwas beim auslesen der Nachrichten schief gegangen")

# Konfiguration MQTT
client = mqtt.Client("MVMC")  # create new instance
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address)  # connect to broker

logging.debug("Programm MVMC wurde gestartet")

client.loop_start()
time.sleep(5)
print(maxcellvoltage)
while(1):
    try:
        time.sleep(60)
        if maxcellvoltage <= MaxVoltCell1:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V) liegt unter dem Wert vom Stufe 1 (" + str(MaxVoltCell1) + "V), ")
            print("daher wird maximale Spannung von " + str(MaxVoltStufe1) + "V eingestellt")
            print("Setze " + str(MaxVoltStufe1))
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(MaxVoltStufe1) + ' }')
            time.sleep(120)
        elif maxcellvoltage <= MaxVoltCell2:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 1 (" +str(MaxVoltCell1) + "V), ")
            print("daher wird maximale Spannung von " + str(MaxVoltStufe2) + "V eingestellt")
            print("Setze " + str(MaxVoltStufe2))
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(MaxVoltStufe2) + '}')
        elif maxcellvoltage <= MaxVoltCell3:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 2 (" +str(MaxVoltCell2) + "V), ")
            print("daher wird maximale Spannung von " + str(MaxVoltStufe3) + "V eingestellt")
            print("Setze " + str(MaxVoltStufe3))
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(MaxVoltStufe3) + '}')
        elif maxcellvoltage <= MaxVoltCell4:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 3 (" +str(MaxVoltCell3) + "V), ")
            print("daher wird maximale Spannung von " + str(MaxVoltStufe4) + "V eingestellt")
            print("Setze " + str(MaxVoltStufe4))
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(MaxVoltStufe4) + '}')
        elif maxcellvoltage >= MaxVoltCell4:
            print("Höchste Zelle(" + str(maxcellvoltage) + "V)  liegt über dem Wert vom Stufe 4 (" +str(MaxVoltCell4) + "V), ")
            print("daher wird maximale Spannung von " + str(MaxVoltStufe5) + "V eingestellt")
            print("Setze " + str(MaxVoltStufe5))
            client.publish("W/" + cerboserial + MaxChargeVoltagePath, '{"value": ' + str(MaxVoltStufe5) + '}')

    except Exception as e:
        logging.exception("Programm MVMC ist abgestürzt. (while Schleife)")
        print(e)
        print("Im MVMC Programm ist etwas beim auslesen der Nachrichten schief gegangen")