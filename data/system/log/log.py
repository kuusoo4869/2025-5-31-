import logging
import os
from datetime import datetime

def setup_logger():
    """
    配置日志记录器，实现按日期保存日志，并将日志输出到控制台和文件
    """
    # 创建日志目录
    # 修正日志目录路径为项目data/log/目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 获取当前日期
    current_date = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f'{current_date}.log')

    # 配置日志记录器
    logger = logging.getLogger('main')
    logger.setLevel(logging.DEBUG)

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    # 设置立即刷新模式
    console_handler.terminator = '\n'
    console_handler.flush = lambda: None
    
    # 定义日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 设置日志立即刷新
    logging.root = logger
    logging.basicConfig(handlers=[file_handler, console_handler], level=logging.DEBUG)

    return logger

# 在需要使用日志的地方调用此函数获取日志记录器
logger = setup_logger()