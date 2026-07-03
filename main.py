import customtkinter as ctk
import json
import base64
import os
import subprocess
import sys
import urllib.request
import zipfile
import threading
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# 🛑 Place your Public Key here
PUBLIC_KEY_DATA = """-----BEGIN PUBLIC KEY-----
MIIBITANBgkqhkiG9w0BAQEFAAOCAQ4AMIIBCQKCAQBS3iWmAqsYlQUDQSQd4esO
pRTc96JTkYXk9qg44zHfYg33sbPZZ+9WZwDsHIWTOCPqE+TUTKoRb1f31zPG8yzu
BviwfZkXlcD8GM31GsPINjSWC8QUm7a0wUQQVPyIzLK4ZoVJYkTB9++gQ6eBWTJf
SAiiGjBQPKboWxnOvFDzPAddMCL5eR5DrlJ6POzwMy1wdeLdd0hKvT0LZNl1aLKo
5VLX4GozpyTwnNclrabSAbWKFPKzsFdNIDqYh7qv2xMIC6BKmPn51wXqEd4epoHE
7vBFv/mDJ3TGcgFqUiw+7hTf9SEIhzz2ZdaolxSnQAElI/R7vGCrHjSD2Ti6qheH
AgMBAAE=
-----END PUBLIC KEY-----"""

CONFIG_FILE = "license_config.json"
SERVER_APPS_JSON_URL = "https://githubusercontent.com"

def get_hardware_id():
    try:
        if sys.platform == "win32":
            cmd = "wmic csproduct get uuid"
            uuid_out = subprocess.check_output(cmd, shell=True).decode().split()
            return uuid_out.strip()
        else:
            import uuid
            return str(uuid.getnode())
    except:
        return "DEFAULT_HWID_998877"

class AppStoreForComputer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("App Store for computer")
        self.geometry("900x600")
        self.current_hwid = get_hardware_id()
        self.is_activated = False
        self.apps = []
        self.check_local_activation()
        self.create_base_widgets()
        threading.Thread(target=self.fetch_apps_from_server, daemon=True).start()

    def check_local_activation(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved_data = json.load(f)
                if saved_data.get("hwid") == self.current_hwid:
                    # فحص هل التاريخ المحفوظ محلياً انتهى أم لا
                    expiry_date = datetime.strptime(saved_data.get("expiry_date"), "%Y-%m-%d").date()
                    if datetime.now().date() <= expiry_date:
                        self.is_activated = True
            except:
                self.is_activated = False

    def verify_serial_and_get_days(self, serial_number):
        try:
            raw_packet = base64.b64decode(serial_number.encode('utf-8')).decode('utf-8')
            packet = json.loads(raw_packet)
            data_bytes = packet["data"].encode('utf-8')
            signature = base64.b64decode(packet["signature"].encode('utf-8'))
            license_info = json.loads(packet["data"])
            
            public_key = serialization.load_pem_public_key(PUBLIC_KEY_DATA.encode('utf-8'))
            public_key.verify(signature, data_bytes, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            
            return True, license_info.get("duration_days", 0)
        except:
            return False, 0

    def create_base_widgets(self):
        self.top_bar = ctk.CTkFrame(self, height=60)
        self.top_bar.pack(fill="x", padx=15, pady=10)
        status_text = "✔ Store Fully Activated" if self.is_activated else "❌ Store Non-Activated (Locked)"
        status_color = "#2ec4b6" if self.is_activated else "#e71d36"
        self.status_lbl = ctk.CTkLabel(self.top_bar, text=status_text, text_color=status_color, font=ctk.CTkFont(size=15, weight="bold"))
        self.status_lbl.pack(side="left", padx=20, pady=15)
        if not self.is_activated:
            self.activate_btn = ctk.CTkButton(self.top_bar, text="Activate Full Store", fg_color="#ff9f1c", hover_color="#ffbf69", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.prompt_activation)
            self.activate_btn.pack(side="right", padx=20, pady=15)
        title_label = ctk.CTkLabel(self, text="App Store for computer", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=10)
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=800, height=400, label_text="Updating catalog...")
        self.scrollable_frame.pack(pady=10, fill="both", expand=True)

    def fetch_apps_from_server(self):
        try:
            req = urllib.request.Request(SERVER_APPS_JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                self.apps = json.loads(response.read().decode())
            self.after(0, self.render_apps)
        except:
            self.after(0, lambda: self.scrollable_frame.configure(label_text="❌ Server Connection Error!"))

    def render_apps(self):
        for widget_item in self.scrollable_frame.winfo_children():
            widget_item.destroy()
        self.scrollable_frame.configure(label_text="Available Software Downloads")
        if not self.apps:
            ctk.CTkLabel(self.scrollable_frame, text="No applications available.").pack(pady=20)
            return
        for app in self.apps:
            card = ctk.CTkFrame(self.scrollable_frame)
            card.pack(pady=10, fill="x", padx=20)
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", padx=20, pady=15)
            ctk.CTkLabel(info_frame, text=app["name"], font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(info_frame, text=app["desc"], font=ctk.CTkFont(size=13), text_color="gray").pack(anchor="w")
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(side="right", padx=20, pady=15)
            if self.is_activated:
                btn = ctk.CTkButton(btn_frame, text="Silent Download", fg_color="#2ec4b6", hover_color="#011627", command=lambda a=app: self.start_download_thread(a))
            else:
                btn = ctk.CTkButton(btn_frame, text="Locked - Requires License", state="disabled", fg_color="#cccccc")
            btn.pack()

    def prompt_activation(self):
        dialog = ctk.CTkInputDialog(text="Enter serial key to start your subscription:", title="Activate Store")
        user_code = dialog.get_input()
        if user_code:
            success, duration_days = self.verify_serial_and_get_days(user_code)
            if success:
                # 🧠 هنا نحسب تاريخ الانتهاء من تاريخ اليوم الفعلي للتفعيل
                calculated_expiry = (datetime.now() + timedelta(days=duration_days)).strftime("%Y-%m-%d")
                
                with open(CONFIG_FILE, "w") as f:
                    json.dump({"serial": user_code, "hwid": self.current_hwid, "expiry_date": calculated_expiry}, f)
                
                self.is_activated = True
                self.render_apps()
                self.status_lbl.configure(text="✔ Store Fully Activated", text_color="#2ec4b6")
                if hasattr(self, 'activate_btn'):
                    self.activate_btn.destroy()
                self.show_popup("Success", f"Activated! Your subscription is valid until {calculated_expiry}")
            else:
                self.show_popup("Failed", "Invalid serial key!")

    def start_download_thread(self, app_info):
        t = threading.Thread(target=self.download_and_extract, args=(app_info,))
        t.start()

    def download_and_extract(self, app_info):
        self.show_popup("Download Started", f"Downloading {app_info['name']}...")
        try:
            download_path = os.path.join(os.environ['USERPROFILE'], 'Downloads', app_info['filename'])
            extract_path = os.path.join(os.environ['USERPROFILE'], 'Downloads', app_info['name'])
            urllib.request.urlretrieve(app_info['url'], download_path)
            if app_info['filename'].endswith('.zip'):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                os.remove(download_path)
            self.show_popup("Complete", f"Successfully installed {app_info['name']}!")
        except:
            self.show_popup("Error", "Download failed.")

    def show_popup(self, title, message):
        popup = ctk.CTkToplevel(self)
        popup.title(title)
        popup.geometry("400x180")
        popup.attributes("-topmost", True)
        ctk.CTkLabel(popup, text=message, font=ctk.CTkFont(size=14), wraplength=350).pack(pady=30)
        ctk.CTkButton(popup, text="OK", width=120, command=popup.destroy).pack()

if __name__ == "__main__":
    app = AppStoreForComputer()
    app.mainloop()
