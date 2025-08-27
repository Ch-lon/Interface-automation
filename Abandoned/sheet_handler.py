# 一次处理一个sheet

import os
import json
import openpyxl
import settings
from common.test_data_handler import add_details_handler, modify_details_handler, del_details_handler



def details_sheet_handle(case):
    """
    处理明细增删改类sheet
    :param case: 代表的是每一行的测试用例
    :return:
    """
    request_data = json.loads(case['request_data'])
    file_name = request_data['excelFile']
    path = os.path.join(settings.TEST_FILE_DIR, file_name)
    wb = openpyxl.load_workbook(path)
    all_sheetNames = wb.sheetnames  # 列表
    if any('明细' in name for name in all_sheetNames):
        pass
    details_sheetNames = [item for item in all_sheetNames if isinstance(item, str) and '明细' in item]
    for detailSheet in details_sheetNames:
        if detailSheet == '新增明细':
            add_details_handler(wb, file_name)
        elif detailSheet == '修改明细':
            modify_details_handler(wb, file_name)
        elif detailSheet == '删除明细':
            del_details_handler(wb, file_name)

def education_sheet_handle(case):
    """
    处理学历增删改类sheet
    :param case: 代表的是每一行的测试用例
    :return:
    """
    pass

def talent_sheet_handle(case):
    """
    处理人才现职sheet
    :param case:
    :return:
    """
    pass




if __name__ == '__main__':
    case1 = {'title': '上传成功-一个文件至多只能有三个sheet：新增、删除、修改，每一类更新只能放在同一种sheet中', 'interface': 'upload', 'method': 'post', 'request_data': '{"excelFile" : "1.xlsx", "ignoreexp" : 1}', 'response_headers_Content-Type ': 'application/json; charset=utf-8', 'expect_data': '{"code" : 0, "msg" : "OK"}', 'file_num': 1}
    details_sheet_handle(case1)