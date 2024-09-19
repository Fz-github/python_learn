import csv

def write_dict_list_to_csv(dict_list, file_path):
    """
    将字典列表写入到 CSV 文件中。

    :param dict_list: 字典列表
    :param file_path: 要写入的 CSV 文件的路径
    """
    # 获取字典中的所有键（字段名）
    fieldnames = dict_list[0].keys() if dict_list else []

    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 写入 CSV 文件的头部
        writer.writeheader()

        # 写入数据行
        writer.writerows(dict_list)

# 示例使用
if __name__ == '__main__':
    # 定义字典列表
    dict_list = [
        {"name": "李四", "age": 30},
        {"name": "马冬梅", "age": 28},
        {"name": "张三丰", "age": 35},
        {"name": "王五", "age": 25}
    ]
    
    # 写入 CSV 文件
    file


import json

def write_dict_list_to_json(dict_list, file_path):
    """
    将字典列表写入到 JSON 文件中。

    :param dict_list: 字典列表
    :param file_path: 要写入的 JSON 文件的路径
    """
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(dict_list, json_file, ensure_ascii=False, indent=4)

# 示例使用
if __name__ == '__main__':
    # 定义字典列表
    dict_list = [
        {"name": "李四", "age": 30},
        {"name": "马冬梅", "age": 28},
        {"name": "张三丰", "age": 35},
        {"name": "王五", "age": 25}
    ]
    
    # 写入 JSON 文件
    file_path = 'output.json'
    write_dict_list_to_json(dict_list, file_path)
    
    print(f"Data written to {file_path}")

def desensitize_name(name):
    """
    对姓名进行脱敏处理，保留首尾字符，中间字符替换为星号（*）。

    :param name: 姓名字符串
    :return: 脱敏后的姓名字符串
    """
    if len(name) <= 2:
        # 如果姓名只有一个或两个字符，则不进行脱敏
        return name
    else:
        # 保留首尾字符，中间字符替换为星号
        return name[0] + '*' * (len(name) - 2) + name[-1]

# 示例使用
names = ["李四", "马冬梅", "张三丰", "王五"]
desensitized_names = [desensitize_name(name) for name in names]

print("Desensitized Names:", desensitized_names)


from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import pymysql

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database',
    'charset': 'utf8mb4'
}

# 定义AES加密相关参数
# 注意：密钥和IV应该是保密的，这里仅用于演示
key = b'This is a 32-byte key for AES encryption'
iv = b'And this is the IV'

# 创建AES加密对象
cipher = AES.new(key, AES.MODE_CBC, iv)

def decrypt_data(encrypted_data):
    # 解密数据
    encrypted_bytes = base64.b64decode(encrypted_data)
    decrypted_padded = cipher.decrypt(encrypted_bytes)
    decrypted_data = unpad(decrypted_padded, AES.block_size)
    return decrypted_data.decode('utf-8')

def get_decrypted_id_from_db():
    # 连接数据库
    connection = pymysql.connect(**db_config)
    
    try:
        with connection.cursor() as cursor:
            # 查询数据
            sql = "SELECT `encrypted_id` FROM `your_table` WHERE `id` = 1"  # 假设id=1是你的数据行
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                encrypted_id = result['encrypted_id']
                # 解密身份证号码
                id_number = decrypt_data(encrypted_id)
                return id_number
    finally:
        connection.close()

# 获取解密后的身份证号码
decrypted_id_number = get_decrypted_id_from_db()
print("Decrypted ID Number:", decrypted_id_number)