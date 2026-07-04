import customtkinter as ctk
import json, base64, os, subprocess, sys, urllib.request, threading, webbrowser, http.server, random, string
from datetime import datetime
from urllib.parse import urlparse, parse_qs

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')

CONFIG_FILE = 'license_config.json'
SERVER_APPS_JSON_URL = 'https://github.com' # رابط سيرفر الـ JSON الخاص بك لاحقاً

# --- دالة فك تشفير السيريال الذكية المتوافقة مع كود المولد ---
def decode_secure_serial(serial_number):
    try:
        clean_serial = serial_number.replace('-', '').upper().strip()
        # إعادة بناء حشوة الـ Base32 المقطوعة عند حرف 23
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

# --- سيرفر محلي لاستلام إيميلات تسجيل الدخول من كافة المنصات ---
AUTH_DATA = {}
class OAuthHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): return
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        query = urlparse(self.path).query
        params = parse_qs(query)
        if "user" in params:
            AUTH_DATA['user'] = params['user'][0]
            AUTH_DATA['provider'] = params.get('provider', ['unknown'])[0]
            html = "<html><body style='font-family:sans-serif; text-align:center; padding-top:50px; background:#111; color:#fff;'><h2>✔ تم تسجيل الحساب بنجاح!</h2><p>ارجع إلى المتجر لإكمال التفعيل والكابتشا.</p></body></html>"
        else:
            html = "<html><body style='font-family:sans-serif; text-align:center; padding-top:50px; background:#111; color:#ff4444;'><h2>❌ فشل تسجيل الدخول</h2></body></html>"
        self.wfile.write(html.encode('utf-8'))

def start_local_auth_server():
    try:
        server = http.server.HTTPServer(('localhost', 8080), OAuthHandler)
        server.handle_request()
    except: pass

class AppStoreForWindows(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('App Store For Windows')
        self.geometry('1250(')
        self.geometry('1250x800')
        self.configure(fg_color='#1a1a1a')
        
        self.current_hwid = get_hardware_id()
        self.is_logged_in = False
        self.is_activated = False
        self.username = ""
        self.auth_provider = ""
        self.days_left = 0
        self.apps = []
        
        self.main_container = ctk.CTkFrame(self, fg_color='#111111', corner_radius=0)
        self.main_container.pack(fill='both', expand=True)
        
        self.check_local_login()
        self.show_main_layout()
        threading.Thread(target=self.fetch_apps_from_server, daemon=True).start()

    def check_local_login(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: saved = json.load(f)
                if saved.get('hwid') == self.current_hwid and saved.get('logged_in') and saved.get('is_activated'):
                    # فحص الأيام المتبقية وحسابها تلقائياً بالتواريخ
                    last_check = datetime.strptime(saved.get('last_check_date', datetime.now().strftime("%Y-%m-%d")), "%Y-%m-%d").date()
                    days_passed = (datetime.now().date() - last_check).days
                    self.days_left = max(0, saved.get('days_left', 0) - days_passed)
                    
                    if self.days_left > 0:
                        self.is_logged_in = True
                        self.is_activated = True
                        self.username = saved.get('username', 'User')
                        self.auth_provider = saved.get('provider', '')
            except: pass

    def show_main_layout(self):
        for w in self.main_container.winfo_children(): w.destroy()
        self.sidebar = ctk.CTkFrame(self.main_container, width=70, fg_color='#1e1e1e', corner_radius=0)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        btn_home = ctk.CTkButton(self.sidebar, text="🏠", width=50, height=50, fg_color='#2d2d2d', hover_color='#252525', font=ctk.CTkFont(size=20), command=self.show_home_content)
        btn_home.pack(pady=(20, 10), padx=10)
        
        self.content_area = ctk.CTkFrame(self.main_container, fg_color='#111111', corner_radius=0)
        self.content_area.pack(side='right', fill='both', expand=True)
        self.show_home_content()

    def show_home_content(self):
        for w in self.content_area.winfo_children(): w.destroy()
        top_bar = ctk.CTkFrame(self.content_area, height=70, fg_color='transparent')
        top_bar.pack(fill='x', side='top', padx=40, pady=10)
        
        search_entry = ctk.CTkEntry(top_bar, placeholder_text="🔍 Search Premium Marketing Tools...", width=400, height=35, fg_color='#202020', border_color='#333333', corner_radius=8)
        search_entry.pack(side='left', pady=15)
        
        account_frame = ctk.CTkFrame(top_bar, fg_color='transparent')
        account_frame.pack(side='right', pady=15)
        
        if self.is_logged_in and self.is_activated:
            provider_icon = "🐙" if self.auth_provider == "GitHub" else "🌐"
            lbl_user = ctk.CTkLabel(account_frame, text=f"{provider_icon} {self.username} (Premium: {self.days_left} Days)", font=ctk.CTkFont(size=14, weight='bold'), text_color='#00a3ff')
            lbl_user.pack(side='left', padx=15)
            
            btn_logout = ctk.CTkButton(account_frame, text="Logout", width=80, height=30, fg_color='#262626', hover_color='#ff3333', command=self.logout)
            btn_logout.pack(side='left')
        else:
            btn_login = ctk.CTkButton(account_frame, text="👤 Sign in & Activate", width=160, height=30, fg_color='#0067b8', hover_color='#005da6', font=ctk.CTkFont(weight='bold'), corner_radius=6, command=self.show_login_popup)
            btn_login.pack(side='left')
            
        ctk.CTkLabel(self.content_area, text="Premium Software & Tools", font=ctk.CTkFont(size=26, weight="bold"), text_color="white").pack(anchor="w", padx=40, pady=(20,10))
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)
        self.render_apps_list()

    def show_login_popup(self):
        self.login_win = ctk.CTkToplevel(self)
        self.login_win.title("Multi-Platform Auth & Activation")
        self.login_win.geometry("520x460")
        self.login_win.resizable(False, False)
        self.login_win.configure(fg_color='#1c1c1c')
        self.login_win.transient(self)
        self.login_win.grab_set()
        
        ctk.CTkLabel(self.login_win, text="Step 1: Choose Your Platform Login", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))
        
        platforms = [
            ("🔴 Google Account", "#ea4335", "#d3382c", "Google"),
            ("🔵 Microsoft / Xbox", "#00a4ef", "#008ad2", "Microsoft"),
            ("🐙 GitHub Developer", "#24292e", "#1c1f23", "GitHub"),
            ("🎮 PlayStation Network", "#003087", "#002366", "PlayStation"),
            ("🎮 Steam Community", "#171a21", "#0d0f14", "Steam")
        ]
        
        for text, color, hover, p_id in platforms:
            ctk.CTkButton(self.login_win, text=text, width=280, height=35, fg_color=color, hover_color=hover, font=ctk.CTkFont(weight="bold"), command=lambda pid=p_id: self.trigger_oauth(pid)).pack(pady=4)

    def trigger_oauth(self, provider):
        AUTH_DATA.clear()
        threading.Thread(target=start_local_auth_server, daemon=True).start()
        # توجيه العميل بروابط محاكاة للشركاء؛ يتم ربطها لاحقاً بـ API حقيقي
        url = f"http://localhost:8080/?user=client_success_email@domain.com&provider={provider}"
        webbrowser.open(url)
        
        def watch_auth():
            import time
            for _ in range(30):
                if 'user' in AUTH_DATA:
                    self.username = AUTH_DATA['user']
                    self.auth_provider = AUTH_DATA['provider']
                    self.after(0, self.prompt_captcha_and_serial)
                    return
                time.sleep(1)
        threading.Thread(target=watch_auth, daemon=True).start()

    def prompt_captcha_and_serial(self):
        for w in self.login_win.winfo_children(): w.destroy()
        
        ctk.CTkLabel(self.login_win, text="Step 2: Security Verification", font=ctk.CTkFont(size=16, weight="bold"), text_color="#00a3ff").pack(pady=10)
        
        # كابتشا بشرية عشوائية محلياً لمنع الروبوتات والتخمين
        self.captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        captcha_bg = ctk.CTkFrame(self.login_win, fg_color="#333", width=140, height=40, corner_radius=6)
        captcha_bg.pack(pady=5)
        captcha_bg.pack_propagate(False)
        ctk.CTkLabel(captcha_bg, text=self.captcha_text, font=ctk.CTkFont(size=18, weight="bold", slant="italic"), text_color="#ff9f1c").pack(expand=True)
        
        self.captcha_entry = ctk.CTkEntry(self.login_win, placeholder_text="Type Captcha Here", width=180, justify='center')
        self.captcha_entry.pack(pady=5)
        
        ctk.CTkLabel(self.login_win, text="Step 3: Enter Your Serial Key", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(15, 5))
