from led import led
import time
BUZZER_PIN = 6
buzzer = led(BUZZER_PIN, active_high=1, default=0, is_input=0)

target_time = time.time()+30

while time.time() < target_time:
    time.sleep(0.5)

    buzzer.turn_on()
    time.sleep(0.5)
    buzzer.turn_off()

