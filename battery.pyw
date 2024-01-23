import requests
import tkinter as tk
from tkinter import ttk

def check_status(ip_address):
    url = f"http://{ip_address}/status.xml"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.content
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        return None

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Battery Status Checker")

        self.rescan_label = tk.Label(self.master, text="Press Scan to check battery status every second.")
        self.rescan_label.grid(row=0, column=1)

        self.rescan_button = tk.Button(self.master, text="Scan", command=self.toggle_rescan)
        self.rescan_button.grid(row=0, column=2)

        self.voltage_labels = []
        self.battery_percentages = []
        self.ip_entries = []
        self.devices = {}

        self.row_num = 2
        self.rescan_running = False

        self.add_ip_button = tk.Button(self.master, text="Add Device", command=self.add_ip)
        
        self.load_ips_from_file("battery.conf")

    def load_ips_from_file(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                if ',' not in line:
                    continue
                device, ip = line.strip().split(',')
                self.devices[device] = ip

        self.add_ip(list(self.devices.keys())[0])

    def check_status(self):
        for i in range(len(self.ip_entries)):
            device = self.ip_entries[i].get()
            ip_address = self.devices[device]
            if self.rescan_running:
                status = check_status(ip_address)
                if status is None:
                    self.voltage_labels[i].config(text="N/A")
                    self.battery_percentages[i].config(text="N/A")
                else:
                    v1 = float(status.split(b"<v1>")[1].split(b"</v1>")[0])
                    battery_percentage = int((v1 - 3.25 * 7) / (4.2 * 7 - 3.25 * 7) * 100)
                    self.voltage_labels[i].config(text=f"{v1:.2f}V")
                    self.battery_percentages[i].config(text=f"{battery_percentage}%")
            else:
                self.voltage_labels[i].config(text="N/A")
                self.battery_percentages[i].config(text="N/A")

    def toggle_rescan(self):
        if self.rescan_running:
            self.rescan_running = False
            self.rescan_button.config(text="Scan")
            self.check_status()
        else:
            self.rescan_running = True
            self.rescan_button.config(text="Stop Scan")
            self.start_rescan()

    def start_rescan(self):
        if self.rescan_running:
            self.check_status()
            self.master.after(1000, self.start_rescan)

    def add_ip(self, default_device=None):
        if self.rescan_running:
            self.toggle_rescan()

        device_label = tk.Label(self.master, text=f"Device:")
        device_label.grid(row=self.row_num, column=0, pady=0)

        device_entry = ttk.Combobox(self.master)
        device_entry['values'] = list(self.devices.keys())
        if default_device and default_device in device_entry['values']:
            device_entry.current(device_entry['values'].index(default_device))
        device_entry.grid(row=self.row_num, column=1, pady=0)
        self.ip_entries.append(device_entry)

        voltage_label = tk.Label(self.master, text="N/A", font=("Arial", 12))
        voltage_label.grid(row=self.row_num, column=2, pady=0)
        self.voltage_labels.append(voltage_label)

        battery_percentage = tk.Label(self.master, text="N/A", font=("Arial", 24))
        battery_percentage.grid(row=self.row_num, column=3, pady=0)
        self.battery_percentages.append(battery_percentage)

        self.row_num += 1

        self.add_ip_button.grid(row=self.row_num, column=2)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
