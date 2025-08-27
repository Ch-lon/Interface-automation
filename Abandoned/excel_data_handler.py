# 用于自动替换测试文件中的唯一标识
# 一次处理一个文件

import os
import json
import openpyxl
import settings
from sheet_handler import details_sheet_handle, education_sheet_handle, talent_sheet_handle


def excelHandler(case):
    """
    修改Excel测试文件
    :param case:
    :return:
    """
    request_data = json.loads(case['request_data'])
    file_name = request_data['excelFile']
    path = os.path.join(settings.TEST_FILE_DIR, file_name)
    wb = openpyxl.load_workbook(path)
    all_sheetNames = wb.sheetnames  # 列表
    if any('明细' in name for name in all_sheetNames):
        details_sheet_handle(case)
    if any('学历' in name for name in all_sheetNames):
        education_sheet_handle(case)
    if '人才现职' in all_sheetNames:
        talent_sheet_handle(case)

    # 保存文件(直接覆盖原文件)
    wb.save(path)




if __name__ == '__main__':
    case1 = {'title': '上传成功-一个文件至多只能有三个sheet：新增、删除、修改，每一类更新只能放在同一种sheet中', 'interface': 'upload', 'method': 'post', 'request_data': '{"excelFile" : "1.xlsx", "ignoreexp" : 1}', 'response_headers_Content-Type ': 'application/json; charset=utf-8', 'expect_data': '{"code" : 0, "msg" : "OK"}', 'file_num': 1}
    excelHandler(case1)