import customtkinter as ctk
import json
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# 🛑 Place your Private Key here
PRIVATE_KEY_DATA = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQBS3iWmAqsYlQUDQSQd4esOpRTc96JTkYXk9qg44zHfYg33sbPZ
Z+9WZwDsHIWTOCPqE+TUTKoRb1f31zPG8yzuBviwfZkXlcD8GM31GsPINjSWC8QU
m7a0wUQQVPyIzLK4ZoVJYkTB9++gQ6eBWTJfSAiiGjBQPKboWxnOvFDzPAddMCL5
eR5DrlJ6POzwMy1wdeLdd0hKvT0LZNl1aLKo5VLX4GozpyTwnNclrabSAbWKFPKz
sFdNIDqYh7qv2xMIC6BKmPn51wXqEd4epoHE7vBFv/mDJ3TGcgFqUiw+7hTf9SEI
hzz2ZdaolxSnQAElI/R7vGCrHjSD2Ti6qheHAgMBAAECggEADX0zy64rg7jeNAVq
h6K6zIt6te1pcwkBLqAoCfqRp7ciZut6Ry1v/DSQJd8Or0Q4NGZAnX5NQMFLJIDX
YM88xRJFcRVA0mICJAc1n2xX6kNIlBQeOuyN9SZwmef7o5kOjo3BrIxefOSLER9y
KNAILxJetWRl8Omukawiq1BkLPOtBIFkiKTYtni6EwCLtNwAPj1N+2Zb8YfMK3oL
/rgKS9ewRe2vUv+YXDIkTtb1xqhmgjdAgjh6R1GlFqOQJC1puYDuzbmANdGB8CEU
nhHj3dx/4LCpkl4+wFIeocBTp0Gj7/JtdpUCx4CALsn96hG25ZOGtIZ/b4amDDNm
h16Q4QKBgQCcjEKGpseS8b8r2QfneiQG2qfWhBt7XbB1arGGUihm2Yt+QVV5mTLx
gEpvfs5cibAGmy1hwSUtPr4B+uakPP7nX5XLXGXkewrMy7NMaCWCafPLza7BbA5v
TUWGuffmDprA9zfVIsOqL+fpBkOpx3CrlgbIOuiqyV/a7tUteJXA5QKBgQCHgx67
Rzzi4KJAXGq1qVLkTLiKpwE0HaBFxfyThvtaNgKrqIqfMGnA7hok0hWaxxEmwmt7
/JlDNb2XioMSnYmTQU4ubGqdVax0+dJQE9cNYCfUxTqJIJrdxMqYvHjcUvI1DxPw
lrTawQmxwS6KjIBQGtB4wSJTWXyPdX86ITmr+wKBgQCFdqrM42loZMPIHSq49Q+7
7DSFFXHclj53jDO3QVoCfVuIkyjNF4gwDmDnd2N1z0kMCMYC/ki0rzYMuBxkT0A+
f+ZUTvzrct79RHkjHfNEoRHhYgSoEHip+WXZ+7hWIYNcGig2hIHuGRONPfL3zvnG
v4weruJnoHEhVNbYAmMh5QKBgGaXBpoDiX29UDhnfsW+xalex8r4OfoJf7+y7s+F
Ph8Ciq0IMMHpdfaAi7xaa868bCiqwZKhHip6sejbDPX33CJmK1kL7P7l0GTSiLzk
+EcBB8aV9gXAcF36UOKmtN0f0owGuTLH9W0y/TLcLG7phW6fjjoNBP6S3bEB4+rP
IoknAoGAaAwR3Y35PaipEu4LsARH2NopjrZQ2Dy2qxhGMh3JEqN96LjSRMoW2a/h
v2ZADp0fctk+cJboVbbYBZN3CY8y4p3BT4b96+AC9PbcvzqK9z/akLwvkopOXv6Q
CZXKZIFLA7Urcnh579WvZ398DnnInuXePRW1PoQOjBjzokv/3Vk=
-----END RSA PRIVATE KEY-----"""

class KeyGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Premium License Key Generator")
        self.geometry("600x520")
        
        ctk.CTkLabel(self, text="App Store Key Generator Panel", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(self, text="Client Email Address:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.email_entry = ctk.CTkEntry(self, width=400, placeholder_text="customer@email.com")
        self.email_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Select Subscription Plan:", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.plan_var = ctk.StringVar(value="30") # القيمة تعبر عن عدد الأيام
        
        self.radio_month = ctk.CTkRadioButton(self, text="1 Month Plan ($25)", variable=self.plan_var, value="30")
        self.radio_month.pack(pady=3)
        self.radio_year = ctk.CTkRadioButton(self, text="1 Year Plan ($70)", variable=self.plan_var, value="365")
        self.radio_year.pack(pady=3)
        self.radio_lifetime = ctk.CTkRadioButton(self, text="Lifetime Access Plan ($100)", variable=self.plan_var, value="99999")
        self.radio_lifetime.pack(pady=3)
        
        self.gen_btn = ctk.CTkButton(self, text="Generate Secure Serial Key", fg_color="#2ec4b6", text_color="white", font=ctk.CTkFont(weight="bold"), command=self.generate_serial)
        self.gen_btn.pack(pady=20)
        
        ctk.CTkLabel(self, text="Generated Serial Key (Activates on first use):", font=ctk.CTkFont(size=14)).pack(pady=5)
        self.result_text = ctk.CTkTextbox(self, width=500, height=120)
        self.result_text.pack(pady=5)

    def generate_serial(self):
        email = self.email_entry.get().strip()
        days = self.plan_var.get()
        if not email:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "Error: Please enter email!")
            return
        try:
            # نضع عدد الأيام كصلاحية وليس تاريخاً ثابتاً
            license_data = {"email": email, "duration_days": int(days), "access": "all_apps"}
            data_bytes = json.dumps(license_data).encode('utf-8')
            private_key = serialization.load_pem_private_key(PRIVATE_KEY_DATA.encode('utf-8'), password=None)
            signature = private_key.sign(data_bytes, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            final_packet = {"data": json.dumps(license_data), "signature": base64.b64encode(signature).decode('utf-8')}
            serial_number = base64.b64encode(json.dumps(final_packet).encode('utf-8')).decode('utf-8')
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", serial_number)
        except Exception as e:
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", f"Error: {str(e)}")

if __name__ == "__main__":
    app = KeyGeneratorApp()
    app.mainloop()
