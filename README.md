

# 数仓数据上传&质检接口自动化

## 项目简介
本项目采用Python+unittest+ddt+psycopg2+openpyxl+allure框架结构，实现数仓数据上传接口与质检接口的自动化测试。


## 项目目录结构

├── main.py                # 主程序入口
├── settings.py            # 配置文件
├── README.md              # 项目说明
├── allure-result/         # 测试报告存储路径
├── common/                # 通用工具代码
│   ├── base_test_case.py  # 提供测试基类和类方法
│   ├── db_handler_Optimization.py  # 数据库查询方法（连接池实现并发）
│   ├── log_handler.py     # 日志记录模块
│   ├── request_handler.py # 接口请求发送方法
│   ├── test_data_handler.py # 测试用例提取、格式处理及批注提取
│   └── test_excel_updater.py # 暂未使用，用于更新测试Excel文件
├── libs/                  # 外部依赖库代码
│   └── my_ddt.py          # 参数化实现
├── log/                   # 日志文件
│   └── SC.log             # 系统日志记录
├── test_cases/            # 接口测试代码
│   ├── test_01_inspection.py # 质检接口测试逻辑
│   └── test_02_upload.py  # 数据上传接口测试逻辑
└── test_data/             # 测试数据
    ├── error_file/        # 异常Excel文件存储
    ├── test_file/         # 接口参数Excel文件存储
    └── cases.xlsx         # 测试用例文件（含两个sheet：inspection/upload）


## 关键模块说明
### 1. common 通用工具模块
- **base_test_case.py**  
  提供测试基类，封装测试初始化、清理等通用方法。
- **db_handler_Optimization.py**  
  基于连接池实现数据库并发查询，支持高效数据校验。
- **log_handler.py**  
  统一日志记录格式，将日志输出到文件`log/SC.log`。
- **request_handler.py**  
  封装接口请求发送逻辑，支持HTTP/HTTPS协议。
- **test_data_handler.py**  
  - 从Excel（`test_data/cases.xlsx`）提取测试用例  
  - 提供数据格式处理函数  
  - 提取Excel批注用于断言判断
- **test_excel_updater.py**  
  （暂未启用）用于更新`test_data/test_file`目录下的测试Excel文件，支持接口重复性校验。

### 2. libs 依赖库模块
- **my_ddt.py**  
  实现数据驱动测试（DDT），支持从Excel文件动态加载测试数据。

### 3. 测试用例与数据
- **test_cases/**  
  按接口功能分文件编写测试逻辑，如：  
  - `test_01_inspection.py`：质检接口测试  
  - `test_02_upload.py`：数据上传接口测试  
- **test_data/cases.xlsx**  
  - **inspection sheet**：质检接口测试用例  
  - **upload sheet**：数据上传接口测试用例  
- **test_data/error_file/**  
  存储接口返回的异常Excel文件，用于错误场景验证。  
- **test_data/test_file/**  
  存放作为接口参数的Excel测试文件。


## 使用说明
1. **环境依赖**  
   - Python 3.x  
   - 依赖库：`unittest`, `ddt`, `psycopg2`, `openpyxl`, `allure-pytest`  
   - 可通过`pip install -r requirements.txt`安装（需自行创建依赖文件）。

2. **运行测试**  
   ```bash
   # 执行所有测试用例
   python main.py
   
   # 在终端查看Allure测试报告
   allure serve allure-result
   ```

3. **配置修改**  
   通过`settings.py`文件配置接口地址、数据库连接信息等参数。


## 注意事项
- `test_excel_updater.py`目前未接入框架，如需使用需手动调用。  
- 测试用例Excel文件需按指定格式编写，批注字段用于预期结果断言。
```