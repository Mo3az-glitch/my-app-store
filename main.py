import customtkinter as ctk
import json, base64, os, subprocess, sys, urllib.request, zipfile, threading
from datetime import datetime

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')

CONFIG_FILE = 'license_config.json'
SERVER_APPS_JSON_URL = 'https://github.io'

def decode_secure_serial(serial_number):
    try:
        clean_serial = serial_number.replace('-', '').upper().strip()
        rem = len(clean_serial) % 8
        if rem > 0: clean_serial += '=' * (8 - rem)
        raw_bytes = base64.b32decode(clean_serial.encode())
        decrypted_text = raw_bytes.decode('utf-8', errors='ignore').strip()
        if "#" in decrypted_text:
            return True, int(decrypted_text.split('#')[-1])
    except: pass
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
        self.title('Microsoft Store Windows Premium')
        self.geometry('1150(' if '1150' else '1150x720')
        self.current_hwid = get_hardware_id()
        
        self.is_activated = False
        self.is_paused = False
        self.days_left = 0
        
        self.apps = []
        self.main_container = ctk.CTkFrame(self, fg_color='#0a0a0a', corner_radius=0)
        self.main_container.pack(fill='both', expand=True)
        
        self.update_subscription_state()
        self.show_main_page()
        threading.Thread(target=self.fetch_apps_from_server, daemon=True).start()

    def update_subscription_state(self):
        """تحديث واحتساب الأيام المستهلكة أو التحقق من حالة التجميد الإيقاف"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: saved = json.load(f)
                if saved.get('hwid') == self.current_hwid:
                    self.is_paused = saved.get('is_paused', False)
                    self.days_left = saved.get('days_left', 0)
                    
                    if self.is_paused:
                        self.is_activated = False
                        return
                        
                    # احتساب الأيام المارة منذ آخر فتح للمتجر
                    last_check = datetime.strptime(saved.get('last_check_date'), "%Y-%m-%d").date()
                    days_passed = (datetime.now().date() - last_check).days
                    
                    if days_passed > 0:
                        self.days_left = max(0, self.days_left - days_passed)
                        saved['days_left'] = self.days_left
                        saved['last_check_date'] = datetime.now().strftime("%Y-%m-%d")
                        with open(CONFIG_FILE, 'w') as fw: json.dump(saved, f_w if 'f_w' else fw)
                        
                    if self.days_left > 0:
                        self.is_activated = True
                    else:
                        self.is_activated = False
            except: pass

    def show_main_page(self):
        for w in self.main_container.winfo_children(): w.destroy()
        
        # شريط علوي فخم ومطور يشبه مايكروسوفت ستور الأصلي
        top_bar = ctk.CTkFrame(self.main_container, height=80, fg_color='#141414', corner_radius=0)
        top_bar.pack(fill='x', side='top')
        
        if self.is_activated:
            status_txt = f"✔ Premium Active ({self.days_left} Days Remaining)"
            status_col = "#2ec4b6"
        elif self.is_paused:
            status_txt = f"⏸ Subscription Paused ({self.days_left} Days Frozen)"
            status_col = "#ff9f1c"
        else:
            status_txt = "❌ License Locked (Limited Access)"
            status_col = "#e71d36"
            
        ctk.CTkLabel(top_bar, text=status_txt, text_color=status_col, font=ctk.CTkFont(size=16, weight='bold')).pack(side='left', padx=30, pady=25)
        
        # أزرار التحكم بالاشتراك
        btn_frame = ctk.CTkFrame(top_bar, fg_color='transparent')
        btn_frame.pack(side='right', padx=30, pady=20)
        
        if self.is_activated:
            ctk.CTkButton(btn_frame, text="Pause Subscription", fg_color="#333333", hover_color="#e71d36", font=ctk.CTkFont(weight="bold"), command=self.pause_subscription).pack(side='left', padx=10)
        elif self.is_paused:
            ctk.CTkButton(btn_frame, text="Resume Subscription", fg_color="#ff9f1c", text_color="black", font=ctk.CTkFont(weight="bold"), command=self.resume_subscription).pack(side='left', padx=10)
        else:
            ctk.CTkButton(btn_frame, text="Activate Store", fg_color="#0067b8", hover_color="#005da6", font=ctk.CTkFont(weight="bold"), command=self.prompt_activation).pack(side='left', padx=10)
            
        # واجهة عرض رئيسية جذابة وبطاقات مصممة بعناية
        ctk.CTkLabel(self.main_container, text="Explore Premium Software", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack(anchor="w", padx=40, pady=(30,10))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)
        self.render_apps_list()

    def fetch_apps_from_server(self):
        try:
            req = urllib.request.Request(SERVER_APPS_JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as res: 
                self.apps = json.loads(res.read().decode())
            self.after(0, self.render_apps_list)
        except:
            self.after(0, lambda: ctk.CTkLabel(self.scroll_frame, text="❌ Cloud Catalog Offline. Check Connection.", text_color="red", font=ctk.CTkFont(size=15)).pack(pady=70))

    def render_apps_list(self):
        if not self.apps: return
        for w in self.scroll_frame.winfo_children(): w.destroy()
        
        for app in self.apps:
            # كارد فخم بتصميم انسيابي مستوحى من نظام ويندوز 11
            card = ctk.CTkFrame(self.scroll_frame, fg_color="#18181c", height=95, corner_radius=16, border_width=1, border_color="#252528")
            card.pack(fill="x", pady=10, padx=15)
            card.pack_propagate(False)
            
            ctk.CTkLabel(card, text=app['name'], font=ctk.CTkFont(size=17, weight='bold'), text_color='white').pack(side='left', padx=30)
            ctk.CTkButton(card, text='View Software →', width=150, height=38, fg_color='#252525', hover_color='#0067b8', font=ctk.CTkFont(weight='bold'), command=lambda a=app: self.show_app_details_page(a)).pack(side='right', padx=30, pady=28)

    def show_app_details_page(self, app):
        for w in self.main_container.winfo_children(): w.destroy()
        
        ctk.CTkButton(self.main_container, text="← Windows Store Catalog", width=150, height=36, fg_color="#202020", font=ctk.CTkFont(weight='bold'), command=self.show_main_page).pack(anchor="w", padx=40, pady=25)
        
        box = ctk.CTkFrame(self.main_container, fg_color='#141416', corner_radius=24, border_width=1, border_color="#222225")
        box.pack(fill='both', expand=True, padx=40, pady=10)
        
        ctk.CTkLabel(box, text=app['name'], font=ctk.CTkFont(size=32, weight='bold'), text_color='white').pack(anchor='w', padx=50, pady=35)
        ctk.CTkLabel(box, text=app['desc'], font=ctk.CTkFont(size=16), text_color='#999999', wraplength=800, justify='left').pack(anchor='w', padx=50, pady=10)
        
        if self.is_activated:
            btn = ctk.CTkButton(box, text="Download Safely (Silent Setup)", size=(280, 54), fg_color="#0067b8", hover_color="#005da6", font=ctk.CTkFont(size=15, weight="bold"), corner_radius=10, command=lambda: self.download_app(app))
        else: 
            btn = ctk.CTkButton(box, text="🔒 Activation Key Required", size=(280, 54), state="disabled", fg_color="#2c2c2e", text_color="#555557", corner_radius=10)
        btn.pack(anchor='w', padx=50, pady=60)

    def prompt_activation(self):
        dialog = ctk.CTkInputDialog(text='Enter your Serial Key (XXXXX-XXXXX-XXXXX):', title='License Activation')
        code = dialog.get_input()
        if code:
            success, duration_days = decode_secure_serial(code.strip())
            if success:
                with open(CONFIG_FILE, 'w') as f: 
                    json.dump({'serial': code.strip(), 'hwid': self.current_hwid, 'days_left': duration_days, 'is_paused': False, 'last_check_date': datetime.now().strftime("%Y-%m-%d")}, f)
                self.update_subscription_state()
                self.show_main_page()
                self.show_popup('Activated', f'Successfully Activated! Total Days Granted: {duration_days}')
            else: self.show_popup('Failed', 'Invalid Subscription License Key!')

    def pause_subscription(self):
        """تجميد الوقت وحفظ الأيام الباقية"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: saved = json.load(f)
            saved['is_paused'] = True
            saved['last_check_date'] = datetime.now().strftime("%Y-%m-%d")
            with open(CONFIG_FILE, 'w') as fw: json.dump(saved, fw)
            self.update_subscription_state()
            self.show_main_page()
            self.show_popup('Subscription Paused', 'Your remaining days are now frozen safely!')

    def resume_subscription(self):
        """فك التجميد وإعادة المزامنة من تاريخ اليوم الجديد"""
        dialog = ctk.CTkInputDialog(text='Re-enter your Serial Key to resume access:', title='Resume Subscription')
        code = dialog.get_input()
        if code:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f: saved = json.load(f)
                if saved.get('serial') == code.strip():
                    saved['is_paused'] = False
