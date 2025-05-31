import json
from pathlib import Path

def load_config():
    """
    加载配置文件
    
    返回:
        dict: 包含配置信息的字典，若文件不存在返回默认配置
    """
    config_path = Path(__file__).parent.parent.parent / 'config.json'
    default_config = {
        "sub_group_ratio": 20,
        "window_width": 700,
        "window_height": 700
    }
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config