import hashlib
import base64
import json
import requests
from datetime import datetime
import pytz
from tkinter import Tk, Label
from PIL import Image, ImageTk
from io import BytesIO

def display_qr_code(base64_qr_code):
    try:
        qr_code_bytes = base64.b64decode(base64_qr_code)
        qr_code_image = Image.open(BytesIO(qr_code_bytes))
        qr_code_photo = ImageTk.PhotoImage(qr_code_image)
        qr_code_label = Label(image=qr_code_photo)
        qr_code_label.image = qr_code_photo 
        qr_code_label.pack()
    except Exception as ex:
        print(f"Error displaying QR code: {ex}")

def generate_signature(payload, secret):
    signature = payload + secret
    
    hash_object = hashlib.sha256(signature.encode())
    hash_bytes = hash_object.digest()
    
    uppercase_signature = hash_bytes.hex().upper()
    base64_encoded_signature = base64.b64encode(bytes.fromhex(uppercase_signature)).decode()
    return base64_encoded_signature

def main():
    singapore_tz = pytz.timezone('Asia/Singapore')
    singapore_datetime = datetime.now(singapore_tz)
    
    transaction_time = singapore_datetime.strftime('%H%M%S')  # Format: HHMMSS
    transaction_date = singapore_datetime.strftime('%m%d')    # Format: MMDD
    
    payload_old = '{"mti":"0200","process_code":"990000","amount":"1000","stan":"100001","transaction_time":"{transaction_time}","transaction_date":"{transaction_date}","entry_mode":"000","condition_code":"85","institution_code":"20000000001","host_tid":"37066801","host_mid":"11137066800","npx_data":{"E103":"37066801","E201":"00000123","E202":"SGD"},"communication_data":[{"type":"http","category":"URL","destination":"https://your-domain-name:8801/demo/order/notification","addon":{"external_API_keyID":"8bc63cde-2647-4a78-ac75-d5f534b56047"}}],"getQRCode":"Y"}'
    payload = payload_old.replace("{transaction_time}", transaction_time).replace("{transaction_date}", transaction_date)
    print(payload)
    secret_key = "16c573bf-0721-478a-8635-38e53e3badf1"
    
    signature = generate_signature(payload, secret_key)
    
    print(f'Signature: {signature}')
    
    url = "https://uat-api.nets.com.sg:9065/uat/merchantservices/qr/dynamic/v1/order/request"
    headers = {
        "KeyId": "231e4c11-135a-4457-bc84-3cc6d3565506",
        "Sign": signature,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        print(f'Response: {response.text}')
        response_text = response.text
        data = json.loads(response_text)
        qrcode = data.get('qr_code')
        root = Tk()
        root.title("QR Code Display")
        display_qr_code(qrcode)
        root.mainloop()
    else:
        print(f'Request failed with status code {response.status_code}: {response.text}')

if __name__ == "__main__":
    main()
