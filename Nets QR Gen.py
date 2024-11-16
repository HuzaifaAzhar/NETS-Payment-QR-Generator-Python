import requests
import hashlib
import base64
import json
from datetime import datetime
import tempfile
import webbrowser
from PIL import Image
from io import BytesIO

# Replace with actual NETS-provided credentials and URLs
API_URL_BASE = "https://uat-api.nets.com.sg/uat/merchantservices"
API_KEY_ID = "231e4c11-135a-4457-bc84-3cc6d3565506"
API_SECRET = "16c573bf-0721-478a-8635-38e53e3badf1"

def generate_signature(payload, secret):
    """
    Generate SHA256 HMAC signature for the payload with the secret key.
    """
    concatenated = payload + secret
    sha256_hash = hashlib.sha256(concatenated.encode()).digest()
    result = base64.b64encode(sha256_hash).decode()
    return base64.b64encode(sha256_hash).decode()

def send_request(api_path, payload):
    """
    Send a POST request to the specified NETS API endpoint.
    """
    payload_json = json.dumps(payload, separators=(',', ':'))
    signature = generate_signature(payload_json, API_SECRET)

    headers = {
        "KeyId": API_KEY_ID,
        "Sign": signature,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(f"{API_URL_BASE}{api_path}", headers=headers, data=payload_json)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API call: {e}")
        return None

def create_order_request(amount, invoice_ref, destination_url):
    """
    Send an order request to NETS API to generate a QR code.
    """
    now = datetime.now()
    payload = {
        "mti": "0200",
        "process_code": "990000",
        "amount": f"{int(amount * 100):012}",
        "stan": "100001",
        "transaction_time": now.strftime("%H%M%S"),
        "transaction_date": now.strftime("%m%d"),
        "entry_mode": "000",
        "condition_code": "85",
        "institution_code": "20000000001",
        "host_tid": "37066801",
        "host_mid": "11137066800",
        "getQRCode": "Y",
        "communication_data": [{
            "type": "http",
            "category": "URL",
            "destination": destination_url,
            "addon": {"external_API_keyID": API_KEY_ID}
        }],
        "invoice_ref": invoice_ref,
        "npx_data": {
            "E103": "37066801",
            "E201": f"{int(amount * 100):012}",
            "E202": "SGD"
        }
    }

    response = send_request("/qr/dynamic/v1/order/request", payload)
    if response:
        print("Order Request Response:", json.dumps(response, indent=4))
        if "qr_code" in response:
            display_qr_image(response["qr_code"])
    return response

def query_order(stan, txn_identifier):
    """
    Query the status of an existing order.
    """
    now = datetime.now()
    payload = {
        "mti": "0100",
        "process_code": "330000",
        "stan": stan,
        "transaction_time": now.strftime("%H%M%S"),
        "transaction_date": now.strftime("%m%d"),
        "entry_mode": "000",
        "condition_code": "85",
        "institution_code": "20000000001",
        "host_tid": "37066801",
        "host_mid": "11137066800",
        "txn_identifier": txn_identifier,
        "npx_data": {"E103": "37066801"}
    }

    response = send_request("/qr/dynamic/v1/transaction/query", payload)
    if response:
        print("Order Query Response:", json.dumps(response, indent=4))
    return response

def reverse_order(stan, txn_identifier, amount):
    """
    Reverse an existing order.
    """
    now = datetime.now()
    payload = {
        "mti": "0400",
        "process_code": "990000",
        "amount": f"{int(amount * 100):012}",
        "stan": stan,
        "transaction_time": now.strftime("%H%M%S"),
        "transaction_date": now.strftime("%m%d"),
        "entry_mode": "000",
        "condition_code": "85",
        "institution_code": "20000000001",
        "host_tid": "37066801",
        "host_mid": "11137066800",
        "txn_identifier": txn_identifier,
        "npx_data": {"E103": "37066801"}
    }

    response = send_request("/qr/dynamic/v1/transaction/reversal", payload)
    if response:
        print("Order Reversal Response:", json.dumps(response, indent=4))
    return response

def display_qr_image(qr_code_base64):
    """
    Decode and display the QR code image.
    """
    try:
        qr_image_data = base64.b64decode(qr_code_base64)
        qr_image = Image.open(BytesIO(qr_image_data))

        # Save and open the QR code in a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            qr_image.save(temp_file.name, "PNG")
            print(f"QR Code saved to {temp_file.name}")
            webbrowser.open(temp_file.name)
    except Exception as e:
        print(f"Error displaying QR code: {e}")

# Example usage
if __name__ == "__main__":
    amount = 5.00  # SGD 1.00
    invoice_ref = "INV12345678"  # Unique invoice reference
    destination_url = "https://your-callback-url.com/notify"

    # Step 1: Create Order Request
    order_response = create_order_request(amount, invoice_ref, destination_url)

    # Extract details for further steps
    if order_response:
        stan = order_response.get("stan", "000001")
        txn_identifier = order_response.get("txn_identifier", "")

        # Step 2: Query Order
        query_response = query_order(stan, txn_identifier)

        # Step 3: Reverse Order
        if query_response:
            reverse_order(stan, txn_identifier, amount)
            query_response = query_order(stan, txn_identifier)

