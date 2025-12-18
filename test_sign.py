import hashlib

# 测试数据
params = {
    'cmdId': '',
    'name': '前厅灯光',
    'type': 'control',
    'subType': '灯光',
    'command': '开机',
    'param': '',
    'resource': '',
    'view': '左上角区域',
    'sign': '794BB4346411E3BFFDED046DB75B5135'
}

salt = 'cE0aM0qC0dB4aD2'

# 排除 sign 字段，按 key 字母顺序排序
sorted_items = sorted(
    ((k, v) for k, v in params.items() if k != 'sign'),
    key=lambda x: x[0]
)

# 构建 key1=value1&key2=value2 字符串
sign_string = '&'.join(f'{k}={v}' for k, v in sorted_items)
print(f'排序后的字符串: {sign_string}')

# 加盐
sign_string_with_salt = sign_string + salt
print(f'加盐后的字符串: {sign_string_with_salt}')

# 计算 MD5
calculated_sign = hashlib.md5(sign_string_with_salt.encode()).hexdigest().upper()
print(f'计算得到的sign: {calculated_sign}')
print(f'期望的sign:     {params["sign"]}')
print(f'是否一致: {calculated_sign == params["sign"]}')
