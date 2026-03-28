import hashlib
import json
import uuid
import urllib.request
import urllib.error

def calculate_sign(params: dict, salt: str) -> str:
    """Replicated logic from AEPClient._calculate_sign."""
    # Exclude 'sign' field, sort by key alphabetically
    sorted_items = sorted(
        ((k, v) for k, v in params.items() if k != "sign"),
        key=lambda x: x[0]
    )
    
    def _format_val(val):
        if isinstance(val, list):
            # Compact JSON format, no extra spaces
            return json.dumps(val, ensure_ascii=False, separators=(',', ':'))
        return str(val)

    # Build key1=value1&key2=value2 string
    sign_string = "&".join(f"{k}={_format_val(v)}" for k, v in sorted_items)
    # Add salt and calculate MD5
    sign_string_with_salt = sign_string + salt
    md5_hash = hashlib.md5(sign_string_with_salt.encode()).hexdigest().upper()
    return sign_string, sign_string_with_salt, md5_hash

def test_aep_api(
    base_url: str,
    salt: str,
    params: dict = None,
    send_request: bool = False
):
    """
    Test AEP API signature and connectivity using standard libraries.
    """
    if params is None:
        # Default test params
        params = {
            "cmdId": str(uuid.uuid4()),
            "name": "小米电视",
            "type": "control",
            "subType": "",
            "command": "打开",
            "view": "",
            "resource": ""
        }
    
    # 1. Calculate and Verify Sign
    base_str, salted_str, calculated_sign = calculate_sign(params, salt)
    params["sign"] = calculated_sign
    
    print("-" * 50)
    print("Step 1: Signature Calculation")
    print(f"Base String:   {base_str}")
    print(f"Salted String: {salted_str}")
    print(f"Calculated Sign: {calculated_sign}")
    print("-" * 50)

    # 2. Connectivity Test
    if send_request:
        print("\nStep 2: Sending Request to AEP...")
        print(f"URL: {base_url}")
        
        data = json.dumps(params, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(base_url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        try:
            with urllib.request.urlopen(req, timeout=10.0) as response:
                status_code = response.getcode()
                body = response.read().decode('utf-8')
                print(f"Status Code: {status_code}")
                print(f"Response Body: {body}")
                
                if status_code == 200:
                    try:
                        resp_data = json.loads(body)
                        if resp_data.get("success"):
                            print("\n[SUCCESS] AEP connection verified and successful!")
                        else:
                            print(f"\n[FAILURE] AEP responded with error: {resp_data.get('message')} (code: {resp_data.get('code')})")
                    except json.JSONDecodeError:
                        print("\n[WARNING] Response received but not in JSON format.")
                else:
                    print(f"\n[ERROR] HTTP Error: {status_code}")
                    
        except urllib.error.URLError as e:
            print(f"\n[ERROR] Network request failed: {e}")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {str(e)}")
    else:
        print("\n[SKIP] Step 2: Connectivity test skipped (use send_request=True to run).")

if __name__ == "__main__":
    # CONFIGURATION: Update these values as needed
    # AEP interface URL
    AEP_BASE_URL = "http://127.0.0.1:8088/aep/voice/command" 
    # AEP signature salt
    AEP_SALT = "cE0aM0qC0dB4aD2" 

    # Example parameters
    test_params = {
        "cmdId": str(uuid.uuid4()),
        'name': '小米电视',
        'type': 'control',
        'subType': 'host',
        'command': '1',
        'view': '1',
        'resource': ['5G智慧医疗视频', '5G智慧交通视频', '5G智慧教育视频']
    }
    
    # Run the test
    # Set send_request=True to actually perform the network call
    print("=== AEP Interface Test ===")
    test_aep_api(
        base_url=AEP_BASE_URL, 
        salt=AEP_SALT, 
        params=test_params, 
        send_request=True
    )
