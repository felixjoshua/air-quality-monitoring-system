# air-quality-monitoring-system

# 🌫️ Air Quality Monitoring System (Online)

Proyek ini merupakan hasil dari tugas mata kuliah Internet of Things (IoT) yang dirancang untuk memantau kualitas udara di lingkungan sekitar. Sistem bekerja dengan sensor yang mendeteksi parameter udara dan mengirimkan datanya ke platform cloud agar dapat diakses publik secara daring. Inisiatif ini juga mendukung *Sustainable Development Goals* (SDG) poin 11: **Sustainable Cities and Communities**.

## 🎯 Tujuan Proyek

- Melakukan pengukuran gas berbahaya, suhu, dan kelembaban melalui sensor MQ135 dan DHT22.
- Mengirim data hasil pengukuran ke cloud (ThingSpeak) secara otomatis dan berkala.
- Menyediakan visualisasi data menggunakan Grafana agar mudah dipahami oleh pengguna.
- Memberikan akses informasi kualitas udara kepada masyarakat secara transparan.

## 🧩 Komponen yang Digunakan

| Komponen     | Kegunaan                                                  |
|--------------|-----------------------------------------------------------|
| ESP32        | Unit mikrokontroler dengan kemampuan WiFi                 |
| MQ135        | Sensor untuk mendeteksi kualitas udara (gas berbahaya)    |
| DHT22        | Sensor suhu dan kelembaban                                |
| OLED Display (opsional) | Tampilan langsung di perangkat                 |
| LED RGB (opsional) | Indikator visual untuk status udara                 |
| Breadboard   | Media perakitan sirkuit sementara                         |
| Kabel Jumper | Penghubung antar komponen                                 |
| ThingSpeak   | Platform penyimpanan dan pengiriman data berbasis cloud  |
| Grafana      | Alat untuk visualisasi data dalam bentuk grafik           |

## 🗂️ Diagram Sistem Blok

Sensor dan ESP32 → WiFi → Platform Cloud (ThingSpeak) → Visualisasi (Grafana) → Pengguna (akses data)

![Diagram Sistem Blok](images/sistem-blok.png)

## 📆 Timeline Proyek

Pelaksanaan proyek dirancang dalam 7 minggu, meliputi:

1. Perumusan ide dan perencanaan proyek  
2. Pengadaan komponen serta pengujian awal  
3. Pengaturan koneksi internet dan integrasi cloud  
4. Pengiriman data sensor secara real-time  
5. Integrasi sistem dan pengolahan data di Grafana  
6. Pengujian lapangan serta validasi sistem  
7. Penyusunan dokumentasi akhir dan presentasi  

## 📁 Struktur Direktori

