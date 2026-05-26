	 
 
import time 
import board 
import busio 
import math 
import adafruit_dht 
import paho.mqtt.client as mqtt 

# ThingSpeak MQTT Config 

THINGSPEAK_MQTT_HOST = "mqtt3.thingspeak.com" 
THINGSPEAK_CLIENT_ID = "NSogDx4KGhQIDAUqCxgUERA" 
THINGSPEAK_USERNAME = "NSogDx4KGhQIDAUqCxgUERA" 
THINGSPEAK_PASSWORD = "mFTlEHvmKdSBGQhBJTqbytFk" 
CHANNEL_ID = "3318971" 

# DHT22 Setup
 dht_device = adafruit_dht.DHT22(board.D4) 

# ADS1115 + MQ135 
Setup import adafruit_ads1x15.ads1115 as ads from adafruit_ads1x15.analog_in import AnalogIn i2c = busio.I2C(board.SCL, board.SDA) adc = ads.ADS1115(i2c) chan = AnalogIn(adc, 0) 

# MQ135 Constants	
RL = 10.0 
VC = 5.0 
CLEAN_AIR_FACTOR = 3.6 
ALPHA = 0.02 

 #MQTT Setup 
def on_connect(client, userdata, flags, rc):  
    if rc == 0: 
        print(" Connected to ThingSpeak") 
    else: 
        print("Connection failed:", rc) 
client = mqtt.Client(client_id=THINGSPEAK_CLIENT_ID) 
client.username_pw_set(THINGSPEAK_USERNAME, THINGSPEAK_PASSWORD) 
client.on_connect = on_connect print("Connecting to ThingSpeak...") client.connect(THINGSPEAK_MQTT_HOST, 1883, 60) 
client.loop_start() 

# Functions def calculate_rs(voltage): 
    return RL * ((VC / voltage) - 1) def calculate_ppm(rs, r0): 
    return 116.6020682 * ((rs / r0) ** -2.769034857)def get_aqi(ppm):  
   if ppm <= 800
        return 50, "Good"   
  else if ppm <= 1200: 
        return 100, "Satisfactory"     
else if ppm <= 2000: 
        return 200, "Moderate"      
else if ppm <= 5000:         return 300, "Poor"     
else if ppm <= 10000: 
        return 400, "Very Poor"    
 else
        return 500, "Severe" def average_rs(samples=10): 
    values = []     for _ in range(samples): 
        v = chan.voltage        
 if v > 0: 

            values.append(calculate_rs(v))         
time.sleep(0.1)    
 return sum(values) / len(values) 
 
# Initial Calibration print(“ Calibrating MQ135...") 

rs_avg = average_rs(30) 
R0 = rs_avg / CLEAN_AIR_FACTOR 
print(f"R0: {R0:.2f}") 

# MAIN LOOP 
while True: 
    try: 
        # -------- MQ135 --------         rs = average_rs(5) 
        ppm = calculate_ppm(rs, R0) 
 
        # Auto-calibration 
        R0 = (1 - ALPHA) * R0 + ALPHA * (rs / CLEAN_AIR_FACTOR) 
        aqi, status = get_aqi(ppm) 
 #  DHT22  
        try: 
            temp = dht_device.temperature             hum = dht_device.humidity         except RuntimeError: 
            temp, hum = None, None 
 
       # PRINT          print(f"Temp: {temp}°C | Humidity: {hum}%")         print(f"PPM: {ppm:.2f} | AQI: {aqi} ({status})") 
	 	 
 

        print("-----------------------------") 
 
        #  MQTT SEND          if temp is not None and hum is not None: 
            topic = f"channels/{CHANNEL_ID}/publish" 
                  payload = (                 f"field1={temp:.2f}&"                 f"field2={hum:.2f}&"                 f"field3={ppm:.2f}&"                 f"field4={aqi}" 
            ) 
 
            client.publish(topic, payload)         
    print( “ Data sent to ThingSpeak") 
 
        # ThingSpeak free limit        
 time.sleep(20) 
 
    except KeyboardInterrupt:         
print("Stopped by user")        
 break 

except Exception as e: 
        print("Error:", e)       
  time.sleep(5) 
 
# Cleanup dht_device.exit() client.loop_stop() 
client.disconnect() 
 
 
python thingspeak_all.py 
 
 
 	 
	 
