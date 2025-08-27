import json
import os
import re
import unittest
from urllib.parse import unquote
from typing import Dict, Union

import settings
from common.request_handler import send_request
from libs.my_ddt import ddt, data
from common.base_test_case import BaseTestCase
from common.log_handler import logger
from common.test_data_handler import get_row_all_comments, get_all_sheet_all_comments


@ddt
class TestInspection(BaseTestCase):
    """质检接口测试类（优化版）"""
    name = '质检接口'
    cases = BaseTestCase.load_cases('Inspection')

    # --------------- 辅助方法区 ---------------
    def _parse_expect_data(self, case: Dict) -> Union[Dict, str]:
        """智能解析期望结果（JSON/文本）"""
        expect_data = case['expect_data'].strip()
        try:
            return json.loads(expect_data), True
        except json.JSONDecodeError:
            return expect_data, False

    def _handle_json_response(self, response, expect_data: Union[Dict, str], case: Dict, request_data: Dict):
        """JSON响应处理逻辑"""
        response_data = {'code': response.json().get('code'), 'msg': response.json().get('msg')}

        # 处理不同格式的预期结果
        if isinstance(expect_data, dict):
            # 预期结果是字典，直接比较
            try:
                self.assertEqual(response_data, expect_data)
                logger.info(f"✅ 测试用例{case['id']}断言成功")
            except AssertionError as e:
                self._log_failure_details(case, request_data, expect_data, response_data, e)
                raise
        else:
            # 预期结果是字符串，只比较消息部分
            try:
                self.assertEqual(response_data['msg'], expect_data)
                logger.info(f"✅ 测试用例{case['id']}断言成功")
            except AssertionError as e:
                self._log_failure_details(case, request_data, expect_data, response_data['msg'], e)
                raise

    # 其他方法保持不变...

    # --------------- 测试方法区 ---------------
    @data(*cases)
    def test_inspection_method(self, case):
        """质检接口核心测试方法"""
        request_data = json.loads(case['request_data'])
        expect_data, is_json = self._parse_expect_data(case)

        url = f"{settings.PROJECT_HOST}{settings.INTERFACE['inspection']}"
        file_path = os.path.join(settings.TEST_FILE_DIR, request_data['excelFile'])

        with open(file_path, 'rb') as f:
            files = {'excelFile': f}
            response = send_request(
                url,
                method='POST',
                files=files,
                cookies=settings.AUTH_COOKIE  # 提取固定cookie
            )

            if 'application/json' in response.headers['Content-Type']:
                # 传递request_data到处理方法
                self._handle_json_response(response, expect_data, case, request_data)
            else:
                self._handle_file_response(response, case, request_data)


if __name__ == '__main__':
    unittest.main(testRunner=unittest.TextTestRunner(verbosity=2))