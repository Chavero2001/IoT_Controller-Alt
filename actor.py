import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO # General Purpose Input/Output library
# Define the MQTT broker and topic
#Subscribes to the appropriate MQTT topic
broker_address = "localhost"  # Replace with the Raspberry Pi's IP if not running locally
topic_temp = "tank/heater"  #MQTT topic
topic_levelh = "level/warningh"  #MQTT topic
topic_levell = "level/warningl"  #MQTT topic
topic_quality = "quality/warning" 

# Set up the GPIO mode
GPIO.setmode(GPIO.BCM)

#pin 18 as output
pin_heater=17
pin_pump_out=27
pin_pump_in=22


GPIO.setup(pin_heater, GPIO.OUT)
GPIO.setup(pin_pump_in, GPIO.OUT)
GPIO.setup(pin_pump_out, GPIO.OUT)

GPIO.setwarnings(False)

# Callback functions for MQTT client
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe(topic_temp)
    client.subscribe(topic_levelh)
    client.subscribe(topic_levell)
    client.subscribe(topic_quality)


def on_message(client, userdata, message):
    print(f"Received message on topic '{message.topic}': {message.payload.decode()}")
    if message.topic == topic_temp:
        if message.payload.decode() == "on": #if on, turn on the LED
            GPIO.output(pin_heater, 1)
        if message.payload.decode() == "off": #if off, turn off the LED
            GPIO.output(pin_heater, 0)
    if message.topic == topic_quality:
        if message.payload.decode() == "on": #if on, turn on the LED
            GPIO.output(pin_pump_out, 1)
        if message.payload.decode() == "off": #if off, turn off the LED
            GPIO.output(pin_pump_out, 0)
    if message.topic == topic_levell:
        if message.payload.decode() == "on": #if on, turn on the LED
            GPIO.output(pin_pump_in, 1)
        if message.payload.decode() == "off": #if off, turn off the LED
            GPIO.output(pin_pump_in, 0)

try:
   while True:
      # Create an MQTT client
      client = mqtt.Client()

      # Set up callback functions
      client.on_connect = on_connect
      client.on_message = on_message

      client.connect(broker_address)

      # Start the MQTT client loop to receive messages
      client.loop_forever()
finally:
   GPIO.cleanup()
	
