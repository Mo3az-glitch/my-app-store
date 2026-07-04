import customtkinter as ctk
import random, string, json, os, hashlib, base64

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')

SECRET_PASSWORD = 'MySuperSecretKeyStore2026'
SERVER_KEYS_DB = 'keys_database.json'

def derive_key(password):
    return hashlib.sha256(password.encode()).digest()[:16]

def encrypt_short_serial(duration_days):
    key = derive_key(SECRET_PASSWORD)
    raw_data = f"KEY:{duration_days}"
    padded_data = raw_data.ljust(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(b'0123456789abcdef'), backend=default_backend())
    enc = cipher.encryptor()
    ct = enc.update(padded_data.encode()) + enc.finalize()
    serial = base64.b32encode(ct).decode().replace('=', '')
    # يولد صيغة مقسمة ومحترفة مثل سيريالات الويندوز
    return "-".join([serial[i:i+5] for i in range(0, len(serial), 5)])[:23]

class PricingKeygenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Store Keygen Cloud Dashboard')
        self.geometry('900x550')
        
        ctk.CTkLabel(self, text='Select Subscription License Tier', font=ctk.CTkFont(size=24, weight='bold'), text_color='white').pack(pady=20)
        cards_frame = ctk.CTkFrame(self, fg_color='transparent')
        cards_frame.pack(fill='x', padx=40, pady=10)
        
        m_card = ctk.CTkFrame(cards_frame, fg_color='#202020', width=240, height=260, corner_radius=14)
        m_card.pack(side='left', expand=True, padx=10)
        m_card.pack_propagate(False)
        ctk.CTkLabel(m_card, text='1 MONTH', font=ctk.CTkFont(size=18, weight='bold'), text_color='#2ec4b6').pack(pady=15)
        ctk.CTkLabel(m_card, text='$25', font=ctk.CTkFont(size=36, weight='bold')).pack()
        ctk.CTkLabel(m_card, text='Full access to 36 tools\nLocked to 1 PC device', text_color='gray').pack(pady=15)
        ctk.CTkButton(m_card, text='Select & Generate', fg_color='#2ec4b6', text_color='black', font=ctk.CTkFont(weight='bold'), command=lambda: self.generate_for_plan(30)).pack(side='bottom', pady=20)

        y_card = ctk.CTkFrame(cards_frame, fg_color='#1a2634', width=240, height=280, corner_radius=14, border_width=2, border_color='#0067b8')
        y_card.pack(side='left', expand=True, padx=10)
        y_card.pack_propagate(False)
        ctk.CTkLabel(y_card, text='1 YEAR', font=ctk.CTkFont(size=18, weight='bold'), text_color='#0067b8').pack(pady=15)
        ctk.CTkLabel(y_card, text='$70', font=ctk.CTkFont(size=36, weight='bold')).pack()
        ctk.CTkLabel(y_card, text='Best seller value plan\nFull access for 365 days', text_color='gray').pack(pady=15)
        ctk.CTkButton(y_card, text='Select & Generate', fg_color='#0067b8', font=ctk.CTkFont(weight='bold'), command=lambda: self.generate_for_plan(365)).pack(side='bottom', pady=20)

        l_card = ctk.CTkFrame(cards_frame, fg_color='#202020', width=240, height=260, corner_radius=14)
        l_card.pack(side='left', expand=True, padx=10)
        l_card.pack_propagate(False)
        ctk.CTkLabel(l_card, text='LIFETIME', font=ctk.CTkFont(size=18, weight='bold'), text_color='#ff9f1c').pack(pady=15)
        ctk.CTkLabel(l_card, text='$100', font=ctk.CTkFont(size=36, weight='bold')).pack()
        ctk.CTkLabel(l_card, text='Pay once, unlock forever\nUnlimited software access', text_color='gray').pack(pady=15)
        ctk.CTkButton(l_card, text='Select & Generate', fg_color='#ff9f1c', text_color='black', font=ctk.CTkFont(weight='bold'), command=lambda: self.generate_for_plan(99999)).pack(side='bottom', pady=20)

        self.output_entry = ctk.CTkEntry(self, width=500, height=45, font=ctk.CTkFont(size=16), justify='center', placeholder_text='Your Serial Key Will Appear Here')
        self.output_entry.pack(pady=30)

    def generate_for_plan(self, days):
        # يولد كود مقسم مثل سيريالات تفعيل الويندوز والألعاب
        parts = ["".join(random.choices(string.ascii_uppercase + string.digits, k=5)) for _ in range(4)]
        serial = "-".join(parts)
        self.output_entry.delete(0, 'end')
        self.output_entry.insert(0, serial)

if __name__ == '__main__':
    app = PricingKeygenApp()
    app.mainloop()
