#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 Cloudflare Dynamic DNS Updater - Windows Tray Application
===============================================================================

Author: Ufuk Yavuzer
Created: May 2, 2025
Version: 1.0.0
Description:
    A Python-based application for automatically updating DNS records in 
    Cloudflare with dynamic IP addresses. The app runs in the Windows system 
    tray and checks for IP changes every 15 minutes, updating the Cloudflare 
    DNS records accordingly. All configurations are stored in a `config.txt` 
    file. The app logs activities in a log file for troubleshooting.

Dependencies:
    - requests: For Cloudflare API communication
    - pystray: For creating a system tray application
    - pillow: For image creation used in the system tray icon
    - tkinter: For configuration GUI (first-time setup)
    - PyInstaller: For converting the script into a standalone executable

License: GNU General Public License v3.0

===============================================================================
"""
import requests
import time
import threading
import logging
import json
import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# === LOG AYARLARI ===
logging.basicConfig(
    filename='cloudflare_ddns.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# === Varsayılan yapı ===
default_config = {
    "api_token": "",
    "dns_name": "",
    "record_type": "A",
    "ttl": 120,
    "proxied": False,
    "interval_minutes": 15
}

# === GUI ile ilk kurulum fonksiyonu ===
def prompt_user_for_config():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Ayarlar Gerekli", "İlk kurulum yapılıyor. Lütfen bilgileri girin.")

    config = {}
    config["api_token"] = simpledialog.askstring("API Token", "Cloudflare API Token:", parent=root)
    config["dns_name"] = simpledialog.askstring("DNS Adı", "Güncellenecek tam DNS adı (örnek: sub.domain.com):", parent=root)
    config["record_type"] = simpledialog.askstring("Kayıt Türü", "DNS kayıt türü (örnek: A):", initialvalue="A", parent=root)
    config["ttl"] = simpledialog.askinteger("TTL", "TTL süresi (saniye):", initialvalue=120, parent=root)
    config["proxied"] = messagebox.askyesno("Proxy", "Cloudflare proxy (CDN) aktif olsun mu?")
    config["interval_minutes"] = simpledialog.askinteger("Zaman Aralığı", "Kaç dakikada bir çalışsın?", initialvalue=15, parent=root)

    with open("config.txt", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    messagebox.showinfo("Başarılı", "Ayarlar kaydedildi.")
    return config

# === Config yükle ===
def load_config():
    config_path = os.path.join(os.path.dirname(sys.argv[0]), "config.txt")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Config yüklenemedi ({e}). Yeni ayarlar istenecek.")
        return prompt_user_for_config()

config = load_config()

# === Zone ID bul ===
def get_zone_id(dns_name):
    headers = {
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get("https://api.cloudflare.com/client/v4/zones", headers=headers)
        if response.status_code == 200:
            zones = response.json()["result"]
            for zone in zones:
                if dns_name.endswith(zone["name"]):
                    logging.info(f"Zone bulundu: {zone['name']} (ID: {zone['id']})")
                    return zone["id"]
            logging.error("DNS adıyla eşleşen zone bulunamadı.")
        else:
            logging.error(f"Zone listesi alınamadı: {response.text}")
    except Exception as e:
        logging.error(f"Zone ID alınırken hata oluştu: {e}")
    return None

# === IP adresi al ===
def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except Exception as e:
        logging.error(f"IP alınamadı: {e}")
        return None

# === DNS kayıt ID'si al ===
def get_dns_record_id(zone_id):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json"
    }
    params = {
        "type": config['record_type'],
        "name": config['dns_name']
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["result"]:
                return data["result"][0]["id"]
            else:
                logging.warning("DNS kaydı bulunamadı.")
        else:
            logging.error("DNS kayıtları alınamadı: " + response.text)
    except Exception as e:
        logging.error(f"DNS kaydı sorgulama hatası: {e}")
    return None

# === DNS güncelle ===
def update_dns_record(zone_id, record_id, ip_address):
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {config['api_token']}",
        "Content-Type": "application/json"
    }
    data = {
        "type": config['record_type'],
        "name": config['dns_name'],
        "content": ip_address,
        "ttl": config['ttl'],
        "proxied": config['proxied']
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        if response.status_code == 200 and response.json()["success"]:
            logging.info(f"DNS güncellendi: {config['dns_name']} -> {ip_address}")
        else:
            logging.error(f"DNS güncelleme hatası: {response.text}")
    except Exception as e:
        logging.error(f"DNS güncelleme istisnası: {e}")

# === Ana görev ===
def run_updater():
    zone_id = get_zone_id(config["dns_name"])
    if not zone_id:
        logging.error("Zone ID alınamadı. İşlem iptal.")
        return

    while True:
        ip = get_public_ip()
        if ip:
            record_id = get_dns_record_id(zone_id)
            if record_id:
                update_dns_record(zone_id, record_id, ip)
        time.sleep(config['interval_minutes'] * 60)

# === Sistem tepsisi simgesi ===
def create_image():
    image = Image.new('RGB', (64, 64), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle([16, 16, 48, 48], fill="orange")
    return image

def on_exit(icon, item):
    icon.stop()

def start_tray():
    icon = Icon("Cloudflare DDNS")
    icon.icon = create_image()
    icon.menu = Menu(MenuItem("Çık", on_exit))
    threading.Thread(target=run_updater, daemon=True).start()
    icon.run()

# === Başlat ===
if __name__ == "__main__":
    start_tray()
