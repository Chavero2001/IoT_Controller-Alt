import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime

# configuration of the MQTT system
MQTT_BROKER = "localhost" #the address of the broker
MQTT_CLIENT_ID = "historian-client"
MQTT_TOPIC = "#"

# SQLite Database configuration
DB_FILE = "historian_data.db"

# MQTT client callback for connection - the method that will be run once connected to the broker
def on_connect(client, userdata, flags, rc):
    print("connected to MQTT")
    # subscribe to the topics
    client.subscribe(MQTT_TOPIC)

# MQTT client callback to handle incoming messages
def on_message(client, userdata, msg):
    print("got a message")
    #get the value
    payload = msg.payload.decode()
    #get the topic
    topic = msg.topic
    #get the timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #save all that to the database as a record
    save_to_database(topic, payload, timestamp)

# method to save to the SQLite3 database
def save_to_database(topic, value, timestamp):
    print("saved a message")
    # connect to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # make sure the DB table exists and build it otherwise
    SQL = "CREATE TABLE IF NOT EXISTS historian_data (topic TEXT, payload TEXT, timestamp TEXT)"
    cursor.execute(SQL)

    # save the message to the table
    SQL = "INSERT INTO historian_data (topic, payload, timestamp) VALUES (?,?,?)"
    cursor.execute(SQL, (topic, value, timestamp))

    # confirm the writing and close
    conn.commit()
    conn.close()

#setting up the object
client = mqtt.Client(client_id=MQTT_CLIENT_ID)

#setting up the callback methods
client.on_connect = on_connect
client.on_message = on_message

#setting up the connection to the broker
client.connect(MQTT_BROKER, 1883, 60)

# start the MQTT client loop but let us define further logic
client.loop_start()

try:
    while True:
        #more logic goes here
        pass

except KeyboardInterrupt:
    #disconnect the client from the broker
    client.disconnect()
