import json
import os
from data.system.log.log import logger

DATA_FILE_PATH = 'data/save/data.json'

def load_data():
    """
    从数据文件中加载数据，并记录日志
    """
    try:
        logger.info(f"开始从 {DATA_FILE_PATH} 加载数据")
        if os.path.exists(DATA_FILE_PATH):
            with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
                data = json.load(file)
                logger.info(f"成功从 {DATA_FILE_PATH} 加载数据")
                return data
        else:
            logger.warning(f"{DATA_FILE_PATH} 文件不存在，返回空数据结构")
            return {"mainGroups": []}
    except Exception as e:
        logger.error(f"从 {DATA_FILE_PATH} 加载数据时出错: {e}")
        return {"mainGroups": []}

def save_data(data):
    """
    将数据保存到数据文件中，并记录日志
    """
    try:
        logger.info(f"开始将数据保存到 {DATA_FILE_PATH}")
        if not os.path.exists(os.path.dirname(DATA_FILE_PATH)):
            os.makedirs(os.path.dirname(DATA_FILE_PATH))
        with open(DATA_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            logger.info(f"成功将数据保存到 {DATA_FILE_PATH}")
    except Exception as e:
        logger.error(f"将数据保存到 {DATA_FILE_PATH} 时出错: {e}")