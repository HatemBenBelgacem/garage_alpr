import cv2
import easyocr
import numpy as np
import re
import requests # NEU: Für die Verbindung zur Web-App
from picamera2 import Picamera2
from gpiozero import OutputDevice, Servo
from time import sleep

# --- KONFIGURATION ---
# Trage hier die IP-Adresse des Computers ein, auf dem deine Flask-App läuft!
# Wenn die App auf dem SELBEN Raspberry Pi läuft, nutze "http://127.0.0.1:5000/api/check"
API_URL = "http://192.168.8.119:5001/api/check"

# --- HARDWARE INITIALISIEREN ---
tor_relais = OutputDevice(18, active_high=True, initial_value=False)
schranken_servo = Servo(17) 

print("🚧 [SERVO] Initialisiere Schranke (Startposition ZU)...")
schranken_servo.min()
sleep(1) 
schranken_servo.detach() 

def impuls_tor_oeffnen():
    print("⚙️ [RELAIS] Sende Schaltimpuls an Garagenmotor (Klack!)...")
    tor_relais.on()   
    sleep(1.0)        
    tor_relais.off()  
    
    print("🚧 [SERVO] Schranke wird geöffnet!")
    schranken_servo.max() 
    sleep(1)
    schranken_servo.detach() 
    
    print("⏳ Tor/Schranke ist offen! Pausiere System für 10 Sekunden...")
    sleep(10) 
    
    print("🚧 [SERVO] Schranke wird wieder geschlossen!")
    schranken_servo.min() 
    sleep(1) 
    schranken_servo.detach() 
    
    print("👀 Wächter-Modus wieder aktiv: Warte auf nächstes Fahrzeug...")

# --- SYSTEM-START ---
print("🤖 Initialisiere Texterkennung (EasyOCR)...")
reader = easyocr.Reader(['de'], gpu=False)

print("📸 Kamera wird für Dauerbetrieb gestartet...")
picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()

print("👀 Wächter-Modus aktiv: Warte auf Bewegung...")

letztes_bild = None

try:
    while True:
        frame = picam2.capture_array()
        grau = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        grau = cv2.GaussianBlur(grau, (21, 21), 0)

        if letztes_bild is None:
            letztes_bild = grau
            continue

        delta = cv2.absdiff(letztes_bild, grau)
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        konturen, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bewegung_erkannt = False
        for kontur in konturen:
            if cv2.contourArea(kontur) < 3000:
                continue
            bewegung_erkannt = True
            break
        
        if bewegung_erkannt:
            print("🚗 Bewegung erkannt! Analysiere Text...")
            
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            ocr_results = reader.readtext(frame_bgr)
            
            zugriff_gewaehrt = False
            for (bbox, text, prob) in ocr_results:
                # Wir filtern Sonderzeichen heraus, bevor wir es an die API senden
                text_clean = re.sub(r'[^A-Z0-9]', '', text.upper())
                
                if len(text_clean) < 4:
                    continue # Zu kurz, ignorieren
                
                print(f"👉 KI liest: '{text_clean}' - Frage Server an...")
                
                try:
                    # Sende POST-Request an deine Flask-API
                    response = requests.post(API_URL, json={'platte': text_clean}, timeout=5)
                    daten = response.json()
                    
                    if response.status_code == 200 and daten.get('status') == 'success':
                        if daten.get('authorized') == True:
                            print(f"🔓 [ZUGRIFF ERLAUBT] Willkommen {daten.get('halter')}! ({daten.get('notiz')})")
                            impuls_tor_oeffnen()
                            zugriff_gewaehrt = True
                            break # Tor öffnet, Suche abbrechen
                        else:
                            # Fahrzeug gesperrt oder nicht bekannt
                            print(f"🔒 [ZUGRIFF VERWEIGERT] Server sagt: {daten.get('message')}")
                    else:
                        print("⚠️ Server antwortet mit Fehler.")
                        
                except Exception as e:
                    print(f"❌ Netzwerkfehler zur API: {e}")
            
            if not zugriff_gewaehrt:
                sleep(3) 
            
            frame = picam2.capture_array()
            grau = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            letztes_bild = cv2.GaussianBlur(grau, (21, 21), 0)
            
        else:
            letztes_bild = grau
            
        sleep(0.2) 

except KeyboardInterrupt:
    print("\n🛑 Wächter-Modus manuell beendet.")
    picam2.stop()
    picam2.close()