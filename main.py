import customtkinter as ctk
import json, base64, os, subprocess, sys, urllib.request, zipfile, threading
from datetime import datetime, timedelta

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')

# نظام تشفير فائق الاستقرار لتقصير السيريالات
CONFIG_FILE = 'license_config.json'
# رابط السيرفر السحابي الخاص بحسابك على GitHub Pages لقراءة البرامج
SERVER_APPS_JSON_URL = 'https://github.io'

def decrypt_short_serial(serial_number):
    try:
        clean_serial = serial_number.replace('-', '')
        raw_bytes = base64.b32decode(clean_serial.encode() + b'===')
        decrypted_text = raw_bytes.decode().strip()
        if ":" in decrypted_text:
            duration_days = int(decrypted_text.split(':')[-1])
            return True, duration_days
    except:
        pass
    return False, 0

def get_hardware_id():
    try:
        if sys.platform == 'win32':
            return subprocess.check_output('wmic csproduct get uuid', shell=True).decode().split()[-1].strip()
        import uuid; return str(uuid.getnode())
    except: return 'DEFAULT_HWID_998877'

class AppStoreForComputer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Microsoft Store Premium Edition')
        self.geometry('1000x650')
        self.current_hwid = get_hardware_id()
        self.is_activated = False
        self.apps = []
        self.main_container = ctk.CTkFrame(self, fg_color='#111111')
        self.main_container.pack(fill='both', expand=True)
        self.check_local_activation()
        self.show_main_page()
        threading.Thread(target=self.fetch_apps_from_server, daemon=True).start()

    def check_local_activation(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: saved = json.load(f)
                if saved.get('hwid') == self.current_hwid: self.is_activated = True
            except: self.is_activated = False

    def show_main_page(self):
        for w in self.main_container.winfo_children(): w.destroy()
        top_bar = ctk.CTkFrame(self.main_container, height=70, fg_color='#1f1f1f', corner_radius=0)
        top_bar.pack(fill='x', side='top')
        status_txt = '✔ Premium Access' if self.is_activated else '❌ Locked Edition'
        status_col = '#2ec4b6' if self.is_activated else '#e71d36'
        ctk.CTkLabel(top_bar, text=status_txt, text_color=status_col, font=ctk.CTkFont(size=16, weight='bold')).pack(side='left', padx=20)
        if not self.is_activated:
            ctk.CTkButton(top_bar, text='Activate Store', fg_color='#ff9f1c', text_color='black', font=ctk.CTkFont(weight='bold'), command=self.prompt_activation).pack(side='right', padx=20)
        ctk.CTkLabel(self.main_container, text='Featured Software', font=ctk.CTkFont(size=26, weight='bold'), text_color='white').pack(anchor='w', padx=30, pady=20)
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color='transparent')
        self.scroll_frame.pack(fill='both', expand=True, padx=20, pady=10)
        self.render_apps_list()

    def fetch_apps_from_server(self):
        try:
            req = urllib.request.Request(SERVER_APPS_JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as res: self.apps = json.loads(res.read().decode())
            self.after(0, self.render_apps_list)
        except:
            self.after(0, lambda: ctk.CTkLabel(self.scroll_frame, text='❌ Connection Error to Host Server', text_color='red', font=ctk.CTkFont(size=16)).pack(pady=50))

    def render_apps_list(self):
        if not self.apps: return
        for w in self.scroll_frame.winfo_children(): w.destroy()
        for app in self.apps:
            card = ctk.CTkFrame(self.scroll_frame, fg_color='#202020', height=100, corner_radius=12)
            card.pack(fill='x', pady=8, padx=10)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=app['name'], font=ctk.CTkFont(size=18, weight='bold'), text_color='white').pack(side='left', padx=20)
            ctk.CTkButton(card, text='View Details →', fg_color='#0067b8', hover_color='#005da6', command=lambda a=app: self.show_app_details_page(a)).pack(side='right', padx=20, pady=35)

    def show_app_details_page(self, app):
        for w in self.main_container.winfo_children(): w.destroy()
        ctk.CTkButton(self.main_container, text='← Back to Store', width=120, fg_color='#333333', command=self.show_main_page).pack(anchor='w', padx=30, pady=20)
        box = ctk.CTkFrame(self.main_container, fg_color='#1f1f1f', corner_radius=18)
        box.pack(fill='both', expand=True, padx=30, pady=10)
        ctk.CTkLabel(box, text=app['name'], font=ctk.CTkFont(size=32, weight='bold'), text_color='white').pack(anchor='w', padx=40, pady=30)
        ctk.CTkLabel(box, text=app['desc'], font=ctk.CTkFont(size=16), text_color='gray', wraplength=700, justify='left').pack(anchor='w', padx=40, pady=10)
        if self.is_activated:
            btn = ctk.CTkButton(box, text='Download Now (Silent Install)', size=(250, 50), fg_color='#2ec4b6', font=ctk.CTkFont(size=16, weight='bold'), command=lambda: self.download_app(app))
        else: btn = ctk.CTkButton(box, text='🔒 Premium License Required', size=(250, 50), state='disabled', fg_color='#444444')
        btn.pack(anchor='w', padx=40, pady=50)

    def prompt_activation(self):
        dialog = ctk.CTkInputDialog(text='Enter your Short Serial Key (XXXX-XXXX-XXXX-XXXX):', title='License Activation')
        code = dialog.get_input()
        if code:
            success, duration_days = decrypt_short_serial(code.strip())
            if success:
                calculated_expiry = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%d')
                with open(CONFIG_FILE, 'w') as f: json.dump({'serial': code, 'hwid': self.current_hwid, 'expiry_date': calculated_expiry}, f)
                self.is_activated = True
                self.show_main_page()
                self.show_popup('Success', f'Activated! Subscription valid until {calculated_expiry}')
            else: self.show_popup('Failed', 'Invalid Serial Key!')

    def download_app(self, app):
        self.show_popup('Downloading', f'Downloading {app["name"]} quietly in background...')
        def worker():
            try:
                path = os.path.join(os.environ['USERPROFILE'], 'Downloads', app['filename'])
                urllib.request.urlretrieve(app['url'], path)
                self.show_popup('Complete', f'Successfully saved {app["name"]} inside Downloads folder!')
            except: self.show_popup('Error', 'Download failed.')
        threading.Thread(target=worker, daemon=True).start()

    def show_popup(self, title, message):
        p = ctk.CTkToplevel(self); p.title(title); p.geometry('350x150'); p.attributes('-topmost', True)
        ctk.CTkLabel(p, text=message, font=ctk.CTkFont(size=14), wraplength=300).pack(pady=25)
        ctk.CTkButton(p, text='OK', width=100, command=p.destroy).pack()

if __name__ == '__main__':
    app = AppStoreForComputer()
    app.mainloop()
