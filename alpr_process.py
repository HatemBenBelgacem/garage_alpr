import cv2
from picamera2 import Picamera2
from ultralytics import YOLO

print("🤖 Lade YOLOv8 KI-Modell...")
# Wir nutzen das 'nano'-Modell, das perfekt auf dem Pi 5 in Echtzeit läuft
model = YOLO("yolov8n.pt") 

print("📸 Nehme Bild für die KI auf...")
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
picam2.start()

frame = picam2.capture_array()
frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

picam2.stop()
picam2.close()

print("🔍 Starte Objekterkennung...")
# Das Modell analysiert das Bild
results = model(frame_bgr)

# Ergebnisse auf dem Bild einzeichnen und speichern
for r in results:
    annotated_frame = r.plot()
    cv2.imwrite("ki_ergebnis.jpg", annotated_frame)

print("✅ Analyse abgeschlossen! Schau dir 'ki_ergebnis.jpg' an.")