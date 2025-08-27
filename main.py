# import unittest
# from test_cases.test_01 import TestInspection
#
# if __name__ == '__main__':
#     # 可以设置 verbosity 来显示更详细的测试信息
#     runner = unittest.TextTestRunner(verbosity=2)
#     suite = unittest.TestLoader().loadTestsFromTestCase(TestInspection)
#     runner.run(suite)

# import pytest
# import settings
#
#
# if __name__ == '__main__':
#
#     pytest.main(['-s', '-v',
#                  '--clean-alluredir',
#                  '--alluredir={}'.format(settings.ALLURE_RESULT_DIR),
#                  'test_cases'])



import pytest
import settings

if __name__ == '__main__':
    pytest.main([
        '-s', '-v',
        '--clean-alluredir',
        f'--alluredir={settings.ALLURE_RESULT_DIR}',  # Allure 报告路径
        '--junitxml=./allure-junit.xml',  # 明确相对路径（当前工作空间，与 Jenkins 工作目录一致）
        'test_cases'
    ])