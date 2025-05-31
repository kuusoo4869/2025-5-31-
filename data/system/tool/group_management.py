import os
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from data.system.log.log import logger
from data.system.tool.data_persistence import save_data

def add_main_group(data, main_group_list):
    """
    添加主分组到数据结构和 UI 列表中
    """
    group_name, ok = QInputDialog.getText(None, "添加主分组", "请输入主分组名称:")
    if ok and group_name:
        # 数据验证：检查主分组名称是否重复
        for group in data["mainGroups"]:
            if group["name"] == group_name:
                QMessageBox.warning(None, "错误", "主分组名称已存在，请选择其他名称。")
                return
        new_id = 1
        if data["mainGroups"]:
            new_id = max(group["id"] for group in data["mainGroups"]) + 1
        new_group = {
            "id": new_id,
            "name": group_name,
            "subGroups": []
        }
        data["mainGroups"].append(new_group)
        main_group_list.addItem(group_name)
        save_data(data)
        logger.info(f"成功添加主分组: {group_name}")

def add_sub_group(data, main_group_list, sub_group_list, selected_main_index):
    """
    添加子分组到数据结构和 UI 列表中
    """
    group_name, ok = QInputDialog.getText(None, "添加子分组", "请输入子分组名称:")
    if ok and group_name:
        main_group = data["mainGroups"][selected_main_index]
        # 数据验证：检查子分组名称是否重复
        for sub_group in main_group["subGroups"]:
            if sub_group["name"] == group_name:
                QMessageBox.warning(None, "错误", "子分组名称已存在，请选择其他名称。")
                return
        new_id = 1
        if main_group["subGroups"]:
            new_id = max(sub_group["id"] for sub_group in main_group["subGroups"]) + 1
        new_sub_group = {
            "id": new_id,
            "name": group_name,
            "files": []
        }
        main_group["subGroups"].append(new_sub_group)
        sub_group_list.addItem(group_name)
        save_data(data)
        logger.info(f"成功添加子分组: {group_name}")