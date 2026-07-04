import customtkinter as ctk
import random, string, base64

ctk.set_appearance_mode('Dark')
ctk.set_default_color_theme('blue')

def generate_dynamic_short_serial(duration_days):
    # توليد ملح عشوائي فريد ومختلف في كل مرة لمنع تكرار الأكواد لنفس الباقة
    random_salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    raw_text = f"{random_salt}#{duration_days}"
    
    encoded_bytes = base64.b32encode(raw_text.encode('utf-8'))
    serial = encoded_bytes.decode('utf-8').replace('=', '').upper()
    
    # تنسيق الكود لمجاميع خماسية احترافية وسهلة للعميل
    formatted = "-".join([serial[i:i+5] for i in range(0, len(serial), 5)])
    return formatted[:23] # قطع الطول عند 23 حرفاً ليعطي شكل مجموعات منظم وثابت

class PricingKeygenApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Store Keygen Cloud Dashboard')
        self.geometry('920x580')
        
        ctk.CTkLabel(self, text='Select Subscription License Tier', font=ctk.CTkFont(size=24, weight='bold'), text_color='white').pack(pady=20)
        
        cards_frame = ctk.CTkFrame(self, fg_color='transparent')
        cards_frame.pack(fill='x', padx=40, pady=10)
        
        # بطاقة باقة الشهر
        m_card = ctk.CTkFrame(cards_frame, fg_color='#1e1e1e', width=250, height=270, corner_radius=16)
        m_card.pack(side='left', expand=True, padx=12)
        m_card.pack_propagate(False)
        ctk.CTkLabel(m_card, text='1 MONTH', font=ctk.CTkFont(size=18, weight='bold'), text_color='#2ec4b6').pack(pady=15)
        ctk.CTkLabel(m_card, text='$25', font=ctk.CTkFont(size=38, weight='bold')).pack()
        ctk.CTkLabel(m_card, text="Full access to 36 tools\nLocked to 1 PC device", text_color="gray", justify="center").pack(pady=15)
        ctk.CTkButton(m_card, text='Select & Generate', fg_color='#2ec4b6', text_color='black', font=ctk.CTkFont(weight='bold'), height=36, command=lambda: self.generate_for_plan(30)).pack(side='bottom', pady=20)

        # بطاقة باقة السنة
        y_card = ctk.CTkFrame(cards_frame, fg_color='#16222f', width=250, height=290, corner_radius=16, border_width=2, border_color='#0067b8')
        y_card.pack(side='left', expand=True, padx=12)
        y_card.pack_propagate(False)
        ctk.CTkLabel(y_card, text='1 YEAR', font=ctk.CTkFont(size=18, weight='bold'), text_color='#0067b8').pack(pady=15)
        y_card.pack_propagate(False)
        ctk.CTkLabel(y_card, text='$70', font=ctk.CTkFont(size=38, weight='bold')).pack()
        ctk.CTkLabel(y_card, text="Best seller value plan\nFull access for 365 days", text_color="gray", justify="center").pack(pady=15)
        ctk.CTkButton(y_card, text='Select & Generate', fg_color='#0067b8', font=ctk.CTkFont(weight='bold'), height=36, command=lambda: self.generate_for_plan(365)).pack(side='bottom', pady=20)

        # بطاقة باقة مدى الحياة
        l_card = ctk.CTkFrame(cards_frame, fg_color='#1e1e1e', width=250, height=270, corner_radius=16)
        l_card.pack(side='left', expand=True, padx=12)
        l_card.pack_propagate(False)
        ctk.CTkLabel(l_card, text='LIFETIME', font=ctk.CTkFont(size=18, weight='bold'), text_color='#ff9f1c').pack(pady=15)
        l_card.pack_propagate(False)
        ctk.CTkLabel(l_card, text='$100', font=ctk.CTkFont(size=38, weight='bold')).pack()
        ctk.CTkLabel(l_card, text="Pay once, unlock forever\nUnlimited software access", text_color="gray", justify="center").pack(pady=15)
        ctk.CTkButton(l_card, text='Select & Generate', fg_color='#ff9f1c', text_color='black', font=ctk.CTkFont(weight='bold'), height=36, command=lambda: self.generate_for_plan(99999)).pack(side='bottom', pady=20)

        ctk.CTkLabel(self, text="Generated Serial Key (Click box below to copy automatically):", font=ctk.CTkFont(size=13), text_color="gray").pack(pady=(25, 0))
        
        # خانة المخرجات التي تدعم ميزة النسخ الفوري بمجرد الضغط عليها
        self.output_entry = ctk.CTkEntry(self, width=520, height=45, font=ctk.CTkFont(size=17, weight="bold"), justify='center', placeholder_text='Your Serial Key Will Appear Here')
        self.output_entry.pack(pady=10)
        self.output_entry.bind("<Button-1>", self.copy_to_clipboard) # ربط حدث الضغط بالنسخ

    def generate_for_plan(self, days):
        serial = generate_dynamic_short_serial(days)
        self.output_entry.delete(0, 'end')
        self.output_entry.insert(0, serial)

    def copy_to_clipboard(self, event):
        serial_text = self.output_entry.get()
        if serial_text and serial_text != "Your Serial Key Will Appear Here":
            self.clipboard_clear()
            self.clipboard_append(serial_text)
            self.update() # تحديث حافظة الويندوز فوراً
            self.show_toast_popup("Copied", "✔ Serial key copied to clipboard successfully!")

    def show_toast_popup(self, title, message):
        toast = ctk.CTkToplevel(self); toast.title(title); toast.geometry('340x110'); toast.attributes('-topmost', True)
        ctk.CTkLabel(toast, text=message, font=ctk.CTkFont(size=13, weight="bold"), text_color="#2ec4b6").pack(pady=20)
        self.after(1500, toast.destroy) # قفل نافذة النسخ تلقائياً بعد ثانية ونصف

if __name__ == '__main__':
    app = PricingKeygenApp()
    app.mainloop()
