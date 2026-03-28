import hashlib
import json

def calculate_sign(params, salt=""):
    # Sort items alphabetically by key, exclude sign
    sorted_items = sorted(
        ((k, v) for k, v in params.items() if k != "sign"),
        key=lambda x: x[0]
    )
    
    def _format_val(val):
        if isinstance(val, list):
            # Same as in aep_client.py
            return json.dumps(val, ensure_ascii=False, separators=(',', ':'))
        return str(val)

    # Build key1=value1&key2=value2 string
    sign_string = "&".join(f"{k}={_format_val(v)}" for k, v in sorted_items)
    # Add salt and calculate MD5
    sign_string_with_salt = sign_string + salt
    return sign_string, sign_string_with_salt, hashlib.md5(sign_string_with_salt.encode()).hexdigest().upper()

# Parameters from log
params = {
    'cmdId': 'fd3d4d2e-c61a-4b2c-8ce8-4c5ffa2d4c26',
    'name': '小米电视',
    'type': 'control',
    'subType': '',
    'command': '',
    'view': '',
    'resource': ['5G智慧医疗视频', '5G智慧交通视频', '5G智慧教育视频']
}

base_str, salted_str, calculated_sign = calculate_sign(params, salt="")
print(f"Base String: {base_str}")
print(f"Salted String: {salted_str}")
print(f"Calculated Sign (no salt): {calculated_sign}")
print(f"Original Sign (from log): 85A665FE8908F7AB5F2832A5D4DB1B08")
