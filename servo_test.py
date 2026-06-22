from gpiozero import Servo
from time import sleep

print("🤖 Starte Servo-Test...")
# Der Servo hängt an GPIO 17 (physisch Pin 11)
schranke = Servo(17)

print("Fahre nach unten (min)...")
schranke.min()
sleep(2)

print("Fahre nach oben (max)...")
schranke.max()
sleep(2)

print("Fahre in die Mitte (mid)...")
schranke.mid()
sleep(2)

print("✅ Test beendet.")