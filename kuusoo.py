import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from data.system.ui.main_window import MainWindow
from data.system.log.log import setup_logger
from data.system.config.config import load_config

def main():
    """
    主函数，用于启动应用程序
    """
    logger = setup_logger()
    logger.info('开始执行主函数')
    app = QApplication(sys.argv)
    # 加载配置
    config = load_config()
    logger.info(f"成功加载配置：{config}")
    
    # 创建主窗口并传递配置
    main_window = MainWindow(config=config)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()