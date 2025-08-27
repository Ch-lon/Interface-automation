import requests
from urllib.parse import unquote  # 解码URL编码的文件名（如%E5%90%8D%E7%A7%B0.xlsx -> 名称.xlsx）
import json
import re
import os

def send_request(url, method = 'GET', **kwargs):
    """
    发送请求
    :param url:
    :param method:
    :param kwargs:
    :return: 响应对象
    """
    method = method.upper()
    if method == 'GET':
        res = requests.get(url, **kwargs)
    elif method == 'POST':
        res = requests.post(url, **kwargs)

    if res.status_code >= 500:
        raise ValueError('服务器错误')
    elif res.status_code >= 400:
        raise ValueError('客户端错误')
    return res

if __name__ == '__main__':
    url1 = 'https://gdw-dev2406s.gaojidata.com/api/v1/detail/check'
    file_path = r"C:\Users\user\Desktop\人才学历新增.xlsx"
    save_path = r"C:\Users\user\Desktop"
    with open(file_path, 'rb') as f:
        files = {'excelFile': f}
        cookies = {
            'authToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjYwNzcxODMsImp0aSI6Imhla3VuLmZlbmcgMyBiMFRKaElFMDRYUUN1cnRVbldGTHRuN081OWpJblI3WUdNSzhFaFRYcEtZPSAyNDYgMiwzLDQiLCJpc3MiOiJoZWt1bi5mZW5nIn0.CP-lUoT4nbxfYKhPnoS9jRbRPbCyu0xhf-pr6XK0pL4'}  # 省略token
        response = send_request(url1, method='POST', files=files, cookies=cookies)

    if 'application/json' in response.headers['Content-Type']:
        print(response.json())
    else:
        # 1. 解析Content-Disposition（关键修复）
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' not in content_disposition:
            filename = '未命名文件.xlsx'
        else:
            # 提取URL编码的JSON字符串
            encoded_json = content_disposition.split('filename=')[-1].strip('"')
            try:
                # 解码并解析JSON（原filename是JSON格式！）
                json_data = json.loads(unquote(encoded_json))
                raw_filename = json_data.get('name', '未命名文件.xlsx')
            except Exception as e:
                print(f"解析文件名失败: {e}，使用原始值")
                raw_filename = unquote(encoded_json)  # 备用方案

        # 2. 清洗文件名（Windows非法字符处理）
        invalid_chars = r'[\\/*?:"<>|]'  # Windows禁止的字符
        sanitized_name = re.sub(invalid_chars, '_', raw_filename)

        # 3. 安全拼接路径（自动补全斜杠）
        save_path = os.path.join(save_path, sanitized_name)  # 自动处理路径分隔符

        # 4. 保存文件（增加异常处理）
        try:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"文件已保存到：{save_path}")
        except Exception as e:
            print(f"保存文件失败: {str(e)}")