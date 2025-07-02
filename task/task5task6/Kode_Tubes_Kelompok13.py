import time
from machine import Pin, ADC
import dht
import network
import urequests
# --- TAMBAHAN UNTUK LCD ---
# Pastikan file esp32_lcd.py sudah ada di ESP32 Anda
from esp32_lcd import GpioLcd 

# --- Konfigurasi ---
WIFI_SSID = "POCO X6 Pro 5G"
WIFI_PASSWORD = "prbprbprb"

BLYNK_AUTH_TOKEN = "NMuxLeXDUphaWp759LKmUCyn2gEhdCVz"
BLYNK_VPIN_TEMP = "v0"
BLYNK_VPIN_HUMIDITY = "v1"
BLYNK_VPIN_AIR_QUALITY = "v2"
BLYNK_SERVER = "blynk.cloud"

THINGSPEAK_WRITE_API_KEY = "KSWGUZ6LS92C05EZ"
THINGSPEAK_API_URL = "https://api.thingspeak.com/update"

# --- TAMBAHAN UNTUK LCD ---
# Inisialisasi LCD sesuai dengan pin yang Anda gunakan
# LiquidCrystal(rs, enable, d4, d5, d6, d7)
try:
    lcd = GpioLcd(rs_pin=Pin(23),
                  enable_pin=Pin(22),
                  d4_pin=Pin(21),
                  d5_pin=Pin(19),
                  d6_pin=Pin(18),
                  d7_pin=Pin(5),
                  num_lines=2, num_columns=16)
    print("LCD berhasil diinisialisasi.")
    lcd.putstr("Air Quality Mon\nSistem Dimulai..") # Pesan Awal
    time.sleep(2)
except Exception as e:
    print(f"Error saat inisialisasi LCD: {e}")
    lcd = None
# --- AKHIR TAMBAHAN LCD ---

time.sleep(1)

dht_sensor = None
mq_sensor = None
ERROR_VALUE_SENSOR = -999

try:
    dht_sensor = dht.DHT22(Pin(2))
    print("Sensor DHT22 berhasil diinisialisasi.")
except Exception as e:
    print(f"Error saat inisialisasi DHT22: {e}")
    dht_sensor = None

try:
    mq_sensor = ADC(Pin(26))
    print("Sensor MQ135 (ADC) berhasil diinisialisasi.")
except Exception as e:
    print(f"Error saat inisialisasi MQ135 (ADC): {e}")
    mq_sensor = None

wlan = network.WLAN(network.STA_IF)

def connect_wifi(ssid, password, activate_interface=True):
    if activate_interface and not wlan.active():
        print("Mengaktifkan antarmuka WiFi...")
        wlan.active(True)
        time.sleep(1)

    if not wlan.isconnected():
        print("Menghubungkan ke WiFi...")
        # --- TAMBAHAN UNTUK LCD ---
        if lcd:
            lcd.clear()
            lcd.putstr("Hubungkan WiFi..")
        # --- AKHIR TAMBAHAN LCD ---
        wlan.connect(ssid, password)
        max_wait = 15
        while not wlan.isconnected() and max_wait > 0:
            print(".", end="")
            time.sleep(1)
            max_wait -= 1
        print()

        if wlan.isconnected():
            print("Terhubung ke WiFi!")
            print(f"Alamat IP: {wlan.ifconfig()[0]}")
            # --- TAMBAHAN UNTUK LCD ---
            if lcd:
                lcd.clear()
                lcd.putstr("WiFi Terhubung!")
                lcd.move_to(0, 1) # Pindah ke baris kedua
                lcd.putstr(wlan.ifconfig()[0])
            # --- AKHIR TAMBAHAN LCD ---
            time.sleep(0.5)
        else:
            print("Gagal terhubung ke WiFi.")
            # --- TAMBAHAN UNTUK LCD ---
            if lcd:
                lcd.clear()
                lcd.putstr("WiFi Gagal!")
            # --- AKHIR TAMBAHAN LCD ---
    return wlan.isconnected()

# ✅ Kirim ke Blynk - per pin
def send_to_blynk(temp, hum, air_quality):
    if not wlan.isconnected():
        print("Blynk: Tidak ada koneksi WiFi. Mencoba menghubungkan...")
        connect_wifi(WIFI_SSID, WIFI_PASSWORD, activate_interface=False)
        if not wlan.isconnected():
            print("Blynk: Gagal terhubung kembali.")
            return

    print("Mengirim data ke Blynk...")
    try:
        base_url = f"http://{BLYNK_SERVER}/external/api/update?token={BLYNK_AUTH_TOKEN}"
        
        # Kirim data dengan jeda singkat
        urequests.get(f"{base_url}&{BLYNK_VPIN_TEMP}={temp}", timeout=10).close()
        time.sleep(0.3)
        urequests.get(f"{base_url}&{BLYNK_VPIN_HUMIDITY}={hum}", timeout=10).close()
        time.sleep(0.3)
        urequests.get(f"{base_url}&{BLYNK_VPIN_AIR_QUALITY}={air_quality}", timeout=10).close()
        print("✅ Data terkirim ke Blynk")

    except Exception as e:
        print(f"❌ Error kirim ke Blynk:", e)

def send_to_thingspeak(temp, hum, air_quality):
    if not wlan.isconnected():
        print("ThingSpeak: Tidak ada koneksi WiFi. Mencoba menghubungkan...")
        connect_wifi(WIFI_SSID, WIFI_PASSWORD, activate_interface=False)
        if not wlan.isconnected():
            print("ThingSpeak: Gagal terhubung kembali.")
            return

    print("Mengirim data ke ThingSpeak...")
    try:
        url = f"{THINGSPEAK_API_URL}?api_key={THINGSPEAK_WRITE_API_KEY}&field1={temp}&field2={hum}&field3={air_quality}"
        response = urequests.get(url, timeout=10)
        print(f"ThingSpeak Server Response: {response.status_code} - {response.text}")
        response.close()
    except Exception as e:
        print(f"Error mengirim ke ThingSpeak: {e}")

connect_wifi(WIFI_SSID, WIFI_PASSWORD, activate_interface=True)
time.sleep(2)

# GANTI SELURUH while True: loop Anda dengan yang ini.

while True:
    try:
        # 1. Baca sensor yang tidak konflik terlebih dahulu (DHT22)
        print("Membaca sensor DHT22...")
        if dht_sensor:
            dht_sensor.measure()
            suhu = dht_sensor.temperature()
            kelembaban = dht_sensor.humidity()
        else:
            suhu = ERROR_VALUE_SENSOR
            kelembaban = ERROR_VALUE_SENSOR

        # 2. Tampilkan data pertama ke LCD SEGERA
        if lcd:
            lcd.clear()
            temp_str = f"Suhu: {suhu:.1f}C" if suhu != ERROR_VALUE_SENSOR else "Suhu: Error"
            lcd.putstr(temp_str)
            
            humi_str = f"H:{kelembaban:.0f}%" if kelembaban != ERROR_VALUE_SENSOR else "H:Err"
            lcd.move_to(16 - len(humi_str), 0) # Taruh di pojok kanan atas
            lcd.putstr(humi_str)

        # 3. Matikan WiFi untuk membaca sensor yang konflik (MQ135)
        print("Menonaktifkan WiFi untuk membaca MQ135...")
        if wlan.isconnected():
            wlan.disconnect()
        if wlan.active():
            wlan.active(False)
        time.sleep(1) # Beri jeda agar WiFi benar-benar mati

        # Baca sensor MQ135
        if mq_sensor:
            kualitas_udara = mq_sensor.read()
        else:
            kualitas_udara = ERROR_VALUE_SENSOR
        
        # 4. Update LCD lagi dengan data kualitas udara
        if lcd:
            lcd.move_to(0, 1)
            air_str = f"K.Udara: {kualitas_udara}" if kualitas_udara != ERROR_VALUE_SENSOR else "K.Udara: Error"
            lcd.putstr(air_str)
        
        print(f"Hasil Baca Sensor -> Suhu: {suhu}, Lembab: {kelembaban}, Udara: {kualitas_udara}")

        # --- PERUBAHAN DI SINI ---
        # Beri jeda agar data di LCD bisa dibaca dengan nyaman
        print("Menahan tampilan data di LCD selama 10 detik...")
        time.sleep(5)
        # --- AKHIR PERUBAHAN ---

        # 5. Aktifkan & hubungkan kembali WiFi untuk mengirim data
        print("Mengaktifkan & menghubungkan kembali WiFi...")
        connect_wifi(WIFI_SSID, WIFI_PASSWORD, activate_interface=True)

        # 6. Kirim data ke Cloud HANYA JIKA terhubung
        if wlan.isconnected():
            print("Koneksi WiFi stabil, mengirim data ke cloud...")
            if lcd:
                lcd.move_to(15, 1) # Pojok kanan bawah
                lcd.putstr(">")    # Indikator: Sedang mengirim

            send_to_blynk(suhu, kelembaban, kualitas_udara)
            send_to_thingspeak(suhu, kelembaban, kualitas_udara)
            
            if lcd:
                lcd.move_to(15, 1)
                lcd.putstr("V") # Indikator: Sukses terkirim

        else:
            print("Tidak terhubung ke WiFi, pengiriman data dilewati.")
            if lcd:
                lcd.move_to(15, 1)
                lcd.putstr("X") # Indikator: Gagal konek

    except Exception as e:
        print(f"Terjadi error besar di loop utama: {e}")
        if lcd:
            lcd.clear()
            lcd.putstr("FATAL ERROR")
            lcd.move_to(0,1)
            lcd.putstr("Restarting...")
            
    # Jeda total sebelum siklus berikutnya dimulai.
    # Total waktu tunggu = 5 detik (tadi) + 10 detik (sekarang) = 15 detik
    print("\nSiklus selesai. Menunggu 10 detik...")
    time.sleep(10)
