# Wiring: ESP32 DevKit + RC522 + MG995 servo

Pins match `rfid_servo_lock.ino`.

## Power
- ESP32 DevKit: USB 5 V (or a regulated 5 V supply on VIN).
- MG995 servo: separate 5-6 V supply rated 2-3 A. Add a 1000 µF capacitor across its V+/GND.
- **Common ground:** the servo supply GND must connect to an ESP32 GND pin.
- RC522: 3.3 V only, from the ESP32 3V3 pin. Never 5 V.

## ESP32 to RC522 (SPI)

| RC522 pin | ESP32 pin |
|-----------|-----------|
| 3.3V      | 3V3       |
| GND       | GND       |
| SDA (SS)  | GPIO 5    |
| SCK       | GPIO 18   |
| MOSI      | GPIO 23   |
| MISO      | GPIO 19   |
| RST       | GPIO 22   |
| IRQ       | not connected |

## ESP32 to servo

| MG995 wire | Connect to |
|------------|-----------|
| Orange (signal) | GPIO 13 |
| Red (V+)   | 5-6 V supply (+) |
| Brown (GND)| 5-6 V supply (-) **and** ESP32 GND |

## Reader placement
The RC522 sits on a separate panel on the frame. Its cable runs to the ESP32 housing. Keep the SPI wires short or twisted with a ground wire to reduce noise.

## Checks before power-up
1. Multimeter: no short between 3V3 and GND.
2. The RC522 gets 3.3 V, not 5 V.
3. The servo signal wire goes to GPIO 13, not 5 V.
4. The servo and ESP32 share a ground.
