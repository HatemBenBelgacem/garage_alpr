import cv2
from picamera2 import Picamera2

print("📸 Starte nativen Picamera2-Test auf Raspberry Pi 5...")

try:
    # 1. Kamera-Instanz erstellen
    picam2 = Picamera2()
    
    # 2. Kamera mit Standard-Konfiguration starten
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()
    print("✓ Kamera erfolgreich gestartet.")
    
    # 3. Ein einzelnes Bild (Frame) aufnehmen
    frame = picam2.capture_array()
    
    # 4. Da Picamera standardmäßig in RGB aufnimmt, OpenCV aber BGR erwartet:
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # 5. Bild speichern
    dateiname = "opencv_test.jpg"
    cv2.imwrite(dateiname, frame_bgr)
    print(f"✅ Bild erfolgreich gespeichert als '{dateiname}'!")
    
    # 6. Kamera sauber schließen
    picam2.stop()
    picam2.close()
    print("Kamera sicher beendet.")

except Exception as e:
    print(f"❌ Fehler beim Kamerazugriff: {e}")