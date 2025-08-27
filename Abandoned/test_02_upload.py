import json
import os
import unittest
from common.base_test_case import BaseTestCase
from libs.my_ddt import ddt, data
from common.request_handler import send_request
from common.test_data_handler import get_all_sheet_all_comments


@ddt
class TestUpload(BaseTestCase):
    name = '上传接口'
    cases = BaseTestCase.load_cases('upload')

    @data(*cases)
    def test_upload_method(self, case):
        """
        上传接口测试方法
        :return:
        """
        # 1. 测试数据
        request_data = json.loads(case['request_data'])
        try:
            expect_data = json.loads(case['expect_data'])  # 字典
        except json.JSONDecodeError:
            expect_data = case['expect_data']
        abnormal_expect_message_count = 0
        abnormal_response_message_count = 0
        # 2. 测试步骤
        url = self.settings.PROJECT_HOST + self.settings.INTERFACE['upload']
        method = case['method']
        test_file_name = request_data['excelFile']
        file_path = os.path.join(self.settings.TEST_FILE_DIR, test_file_name)
        with open(file_path, 'rb') as f:
            files = {'excelFile': f}
            data_int = {'ignoreexp': 0}
            cookies = self.settings.AUTH_COOKIE
            response = send_request(url, method=method, files=files, cookies=cookies, data=data_int).json()
            if response['code'] == 200:
                response_data = {"code": response['code'], "msg": response['msg']}
                try:
                    self.assertEqual(expect_data, response_data)
                except Exception as e:
                    self.assert_log(case, request_data, expect_data=expect_data, response_data=response_data)
                    raise e
                # 入库数据清除
                if case['delete_sql']:
                    delete_sql_row = case['delete_sql'].split(';')
                    delete_sql_list = [s.strip('\n') for s in delete_sql_row if s]
                    for sql in delete_sql_list:
                        self.db.del_data(sql)
                self.success_log(case)
            elif response['code'] == -1:
                error_file_id = response['data']['fileId']
                error_file_name = response['data']['feedBack']['name']
                abnormal_sheet_message = response['data']['feedBack']['exp']['desc']
                basic_validation_failed_sheet_message = response['data']['feedBack']['exp']['basic']
                if any(self.settings.RESPONSE_BASIC_VERIFICATION_FAILED_TEXT in value for value in basic_validation_failed_sheet_message.values()):
                    for v in expect_data.values():
                        try:
                            self.assertIn(v, basic_validation_failed_sheet_message.values())
                        except Exception as e:
                            self.assert_log(case, request_data, expect_data=expect_data, response_data=basic_validation_failed_sheet_message)
                            raise e
                else:
                    for value in abnormal_sheet_message.values():
                        if value != self.settings.RESPONSE_NORMAL_SHEET_TEXT:
                            abnormal_response_message_count += 1
                    abnormal_expect_message_count = len(expect_data)
                    for value in expect_data.values():
                        try:
                            self.assertIn(value, abnormal_sheet_message.values())
                        except Exception as e:
                            self.assert_log(case, request_data, expect_data=expect_data, response_data=abnormal_sheet_message)
                            raise e
                    # 预期的异常提示语数量小于等于实际的
                    try:
                        self.assertLessEqual(abnormal_expect_message_count, abnormal_response_message_count)
                    except Exception as e:
                        self.assert_log(case, request_data, expect_data=expect_data, response_data=abnormal_sheet_message)
                        raise e
                    # 数据入库
                    f.seek(0)
                    response_enter_database = send_request(url, method=method, files=files, cookies=cookies, data={'ignoreexp': 1}).json()
                    try:
                        self.assertEqual(200, response_enter_database['code'])
                    except Exception as e:
                        self.logger.exception(f'{case["id"]}-通过接口入库失败')
                        raise e
                    # 检查数据是否入库
                    if case['search_sql']:
                        search_sql_row = case['search_sql'].split(';')
                        search_sql_list = [s.strip('\n') for s in search_sql_row if s]
                        search_sql_list = [s.strip() for s in search_sql_list if s.strip()]
                        for sql in search_sql_list:
                            db_result = self.db.get_all(sql)[0][0]
                            try:
                                self.assertTrue(db_result)
                            except Exception as e:
                                self.logger.exception(f'{case['id']}-数据库查询失败')
                                raise e
                    if case['search_del_sql']:
                        search_del_sql_row = case['search_del_sql'].split(';')
                        search_del_sql_list = [s.strip('\n') for s in search_del_sql_row if s]
                        for sql in search_del_sql_list:
                            db_result2 = self.db.get_all(sql)
                            try:
                                self.assertFalse(db_result2)
                            except Exception as e:
                                self.logger.exception(f'{case['id']}-删除数据失败')
                                raise e
                    # 清除已入库的测试数据
                    if case['delete_sql']:
                        delete_sql_row = case['delete_sql'].split(';')
                        delete_sql_list = [s.strip('\n') for s in delete_sql_row if s]
                        for sql in delete_sql_list:
                            self.db.del_data(sql)
                # 下载异常文件
                download_url = self.settings.PROJECT_HOST + self.settings.INTERFACE['download']
                json_data = {"id": error_file_id}
                download_response = send_request(download_url, method='POST', json=json_data, cookies=cookies)
                error_file_path = os.path.join(self.settings.ERROR_FILE_SAVE_DIR, error_file_name)
                try:
                    with open(error_file_path, 'wb') as f:
                        f.write(download_response.content)
                        self.logger.info(f'{test_file_name}返回的异常文件已保存，保存路径为：{error_file_path}')
                except Exception as e:
                    self.logger.error(f"保存文件失败: {str(e)}")
                    raise e
                # 进一步断言判断(可选)
                comment_data = get_all_sheet_all_comments(error_file_path)
                comment_data_keys = comment_data.keys()
                for key, value in expect_data.items():
                    for i in comment_data_keys:
                        if key.split('-')[0] == i:
                            try:
                                self.assertEqual(value, comment_data[i])
                            except Exception as e:
                                self.assert_log(case, request_data, expect_data=expect_data,
                                                response_data=abnormal_sheet_message)
                                raise e
                self.success_log(case)

if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner())
