import cv2
import easyocr
from picamera2 import Picamera2
from ultralytics import YOLO

# --- KONFIGURATION ---
# Hier trägst du die erlaubten Kennzeichen ein (deine "Whitelisting-Datenbank")
ERLAUBTE_KENNZEICHEN = ["MA-CH-2026", "B-MW-1234", "VS-CODE-5"]

print("🤖 Initialisiere KI-Modelle (YOLOv8 + EasyOCR)...")
model = YOLO("yolov8n.pt") 
reader = easyocr.Reader(['de'], gpu=False) # 'de' steht für deutsche/europäische Kennzeichen

print("📸 Nehme Bild auf...")
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()
frame = picam2.capture_array()
frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
picam2.stop()
picam2.close()

print("🔍 Scanne nach Objekten...")
results = model(frame_bgr, verbose=False)

# Wir simulieren hier die Erkennung. YOLOv8 erkennt primär "car" (Auto) oder "license plate"
for r in results:
    for box in r.boxes:
        # Klasse 2 bei COCO-Dataset ist ein Auto ('car')
        if int(box.cls[0]) == 2: 
            # Koordinaten des Autos im Bild abgreifen
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Das Auto aus dem Bild ausschneiden, um den Suchbereich für den Text zu verkleinern
            auto_crop = frame_bgr[y1:y2, x1:x2]
            
            print("🔤 Versuche Text/Kennzeichen im Autobereich zu lesen...")
            ocr_results = reader.readtext(auto_crop)
            
            for (bbox, text, prob) in ocr_results:
                # Text bereinigen (Leerzeichen entfernen, alles in Großbuchstaben)
                text_clean = text.replace(" ", "").upper()
                print(f"👉 Text gefunden: '{text_clean}' (Sicherheit: {round(prob*100)}%)")
                
                # Datenbank-Abgleich
                if text_clean in ERLAUBTE_KENNZEICHEN:
                    print(f"🔓 [ZUGRIFF GEWÄHRT] Kennzeichen {text_clean} ist registriert!")
                    print("⚙️ SENDE BEFEHL AN MOTOR: ÖFFNE TOR...")
                    # Hier kommt später die Ansteuerung der GPIO-Pins für den Motor hin
                    break
                else:
                    print(f"🔒 [ZUGRIFF VERWEIGERT] Unbekanntes Fahrzeug: {text_clean}")

print("✅ Durchlauf beendet.")