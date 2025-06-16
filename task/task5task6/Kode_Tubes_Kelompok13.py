import time
from machine import Pin, ADC
import dht
import network
import urequests

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
            time.sleep(0.5)
        else:
            print("Gagal terhubung ke WiFi.")
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

        url_temp = f"{base_url}&{BLYNK_VPIN_TEMP}={temp}"
        print("URL V0:", url_temp)
        res_temp = urequests.get(url_temp, timeout=10)
        print("✅ Terkirim V0:", res_temp.status_code)
        res_temp.close()
        time.sleep(0.3)

        url_hum = f"{base_url}&{BLYNK_VPIN_HUMIDITY}={hum}"
        print("URL V1:", url_hum)
        res_hum = urequests.get(url_hum, timeout=10)
        print("✅ Terkirim V1:", res_hum.status_code)
        res_hum.close()
        time.sleep(0.3)

        url_air = f"{base_url}&{BLYNK_VPIN_AIR_QUALITY}={air_quality}"
        print("URL V2:", url_air)
        res_air = urequests.get(url_air, timeout=10)
        print("✅ Terkirim V2:", res_air.status_code)
        res_air.close()

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

while True:
    suhu = ERROR_VALUE_SENSOR
    kelembaban = ERROR_VALUE_SENSOR
    kualitas_udara = ERROR_VALUE_SENSOR

    try:
        if not wlan.isconnected():
            print("Koneksi WiFi terputus. Mencoba menghubungkan kembali...")
            connect_wifi(WIFI_SSID, WIFI_PASSWORD, activate_interface=False)
            if not wlan.isconnected():
                print("Gagal menghubungkan kembali. Melewati siklus ini.")
                time.sleep(10)
                continue
            else:
                print("Terhubung kembali ke WiFi.")
                time.sleep(2)

        if dht_sensor:
            try:
                dht_sensor.measure()
                suhu = dht_sensor.temperature()
                kelembaban = dht_sensor.humidity()
            except Exception as e_dht:
                print(f"Error membaca DHT22: {e_dht}")
        else:
            print("Sensor DHT22 tidak diinisialisasi.")

        wifi_was_active_for_mq135 = False
        if mq_sensor:
            if wlan.isconnected():
                print("Menonaktifkan WiFi sementara untuk membaca MQ135...")
                wlan.disconnect()
                disconnect_wait = 5
                while wlan.isconnected() and disconnect_wait > 0:
                    print("Menunggu WiFi disconnect...")
                    time.sleep(0.2)
                    disconnect_wait -= 1
                if not wlan.isconnected():
                    print("WiFi berhasil disconnected.")
                    wlan.active(False)
                    time.sleep(0.5)
                    wifi_was_active_for_mq135 = True
            elif wlan.active():
                print("WiFi tidak terhubung tapi aktif, menonaktifkan...")
                wlan.active(False)
                time.sleep(0.5)
                wifi_was_active_for_mq135 = True

            try:
                print("Membaca MQ135...")
                time.sleep(0.5)
                kualitas_udara = mq_sensor.read()
            except Exception as e_mq:
                print(f"Error membaca MQ135: {e_mq}")
        else:
            print("Sensor MQ135 tidak diinisialisasi.")

        if wifi_was_active_for_mq135:
            print("Mengaktifkan kembali WiFi...")
            if not wlan.active():
                wlan.active(True)
                time.sleep(1)

        print(f"Suhu       : {suhu} °C")
        print(f"Kelembaban : {kelembaban} %")
        print(f"Kualitas Udara (MQ135): {kualitas_udara}")
        print("------------------------")

        send_to_blynk(suhu, kelembaban, kualitas_udara)
        send_to_thingspeak(suhu, kelembaban, kualitas_udara)

    except Exception as e:
        print(f"Terjadi error tidak terduga: {e}")
        if not wlan.active():
            print("Mengaktifkan WiFi karena error...")
            wlan.active(True)
            time.sleep(1)
        if not wlan.isconnected():
            connect_wifi(WIFI_SSID, WIFI_PASSWORD, activate_interface=False)

    print("Menunggu 5 detik sebelum siklus berikutnya...\n")
    time.sleep(5)
