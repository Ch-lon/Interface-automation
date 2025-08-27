import logging
import settings

COLOR_MAP = {
    logging.DEBUG: "\033[34m",    # 蓝色
    logging.INFO: "\033[32m",     # 绿色
    logging.WARNING: "\033[33m",  # 黄色
    logging.ERROR: "\033[31m",    # 红色
    logging.CRITICAL: "\033[1;31m"  # 加粗红色
}
RESET_COLOR = "\033[0m"

def get_logger(name='数仓测试日志', file='upload.log',
              fmt='%(levelname)s %(asctime)s [%(filename)s-->line:%(lineno)d]:%(message)s',
              debug=False):
    file_level = logging.DEBUG if debug else logging.WARNING
    console_level = logging.DEBUG if debug else logging.INFO

    logger_ = logging.getLogger(name)
    if logger_.handlers:  # 防止重复添加handler
        return logger_
    logger_.setLevel(logging.DEBUG)

    # 文件处理器（无颜色）
    file_handler = logging.FileHandler(filename=file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter(fmt=fmt))  # 直接使用标准格式化器

    # 控制台处理器（带颜色）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    # 关键修复：通过参数告知是控制台格式化器
    console_formatter = ColorFormatter(fmt=fmt, color_map=COLOR_MAP, reset=RESET_COLOR, is_console=True)
    console_handler.setFormatter(console_formatter)

    logger_.addHandler(file_handler)
    logger_.addHandler(console_handler)
    return logger_

# 修复版彩色格式化器（移除对handler的依赖）
class ColorFormatter(logging.Formatter):
    def __init__(self, fmt, color_map, reset, is_console=False):
        super().__init__(fmt)
        self.color_map = color_map
        self.reset = reset
        self.is_console = is_console  # 通过参数标记是否为控制台

    def format(self, record):
        # 关键修复：使用初始化参数判断，而非访问handler
        if self.is_console:
            color = self.color_map.get(record.levelno, self.reset)
            record.msg = f"{color}{record.msg}{self.reset}"
        return super().format(record)

logger = get_logger(**settings.LOG_CONFIG)

if __name__ == '__main__':
    logger.debug("调试信息 - 蓝色")
    logger.info("正常操作 - 绿色")
    logger.warning("警告信息 - 黄色")
    logger.error("错误信息 - 红色")
    logger.critical("严重错误 - 加粗红色")
