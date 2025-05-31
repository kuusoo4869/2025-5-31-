import json
import os
from data.system.log.log import logger

CONFIG_FILE_PATH = 'data/system/config/config.json'

def load_config():
    """
    从配置文件中加载配置信息，并记录日志
    """
    try:
        logger.info(f"开始从 {CONFIG_FILE_PATH} 加载配置信息")
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
                config = json.load(file)
                logger.info(f"成功从 {CONFIG_FILE_PATH} 加载配置信息")
                return config
        else:
            logger.warning(f"{CONFIG_FILE_PATH} 文件不存在，返回空配置")
            return {}
    except Exception as e:
        logger.error(f"从 {CONFIG_FILE_PATH} 加载配置信息时出错: {e}")
        return {}

def save_config(config):
    """
    将配置信息保存到配置文件中，并记录日志
    """
    try:
        logger.info(f"开始将配置信息保存到 {CONFIG_FILE_PATH}")
        if not os.path.exists(os.path.dirname(CONFIG_FILE_PATH)):
            os.makedirs(os.path.dirname(CONFIG_FILE_PATH))
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=2)
            logger.info(f"成功将配置信息保存到 {CONFIG_FILE_PATH}")
    except Exception as e:
        logger.error(f"将配置信息保存到 {CONFIG_FILE_PATH} 时出错: {e}")