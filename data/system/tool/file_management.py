import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from data.system.log.log import logger
from data.system.tool.data_persistence import save_data

def add_files(data, main_group_list, sub_group_list, file_list, selected_main_index, selected_sub_index):
    """
    添加文件到数据结构和 UI 列表中
    """
    main_group = data["mainGroups"][selected_main_index]
    sub_group = main_group["subGroups"][selected_sub_index]
    existing_file_names = [file["name"] for file in sub_group["files"]]
    new_id = 1
    if sub_group["files"]:
        new_id = max(file["id"] for file in sub_group["files"]) + 1
    file_paths, _ = QFileDialog.getOpenFileNames(None, "选择文件")
    if file_paths:
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            if file_name in existing_file_names:
                QMessageBox.warning(None, "错误", f"文件 {file_name} 已存在，请选择其他文件。")
                continue
            file_size = os.path.getsize(file_path)
            new_file = {
                "id": new_id,
                "name": file_name,
                "size": f"{file_size}B",
                "path": file_path
            }
            sub_group["files"].append(new_file)
            file_list.addItem(file_name)
            new_id += 1
        save_data(data)
        logger.info(f"成功添加 {len(file_paths)} 个文件")

def handle_file_drop(data, main_group_list, sub_group_list, file_list, event):
    """
    处理文件列表的放下事件，将拖入的文件添加到列表中
    """
    selected_main_index = main_group_list.currentRow()
    selected_sub_index = sub_group_list.currentRow()
    if selected_main_index >= 0 and selected_sub_index >= 0:
        main_group = data["mainGroups"][selected_main_index]
        if main_group["subGroups"] and selected_sub_index < len(main_group["subGroups"]):
            sub_group = main_group["subGroups"][selected_sub_index]
            existing_file_names = [file["name"] for file in sub_group["files"]]
            new_id = 1
            if sub_group["files"]:
                new_id = max(file["id"] for file in sub_group["files"]) + 1
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isfile(file_path):
                    file_name = os.path.basename(file_path)
                    # 数据验证：检查文件名称是否重复
                    if file_name in existing_file_names:
                        QMessageBox.warning(None, "错误", f"文件 {file_name} 已存在，请选择其他文件。")
                        continue
                    file_size = os.path.getsize(file_path)
                    new_file = {
                        "id": new_id,
                        "name": file_name,
                        "size": f"{file_size}B",
                        "path": file_path
                    }
                    sub_group["files"].append(new_file)
                    file_list.addItem(file_name)
                    new_id += 1
                    logger.info(f"通过拖动添加文件: {file_name}")
            save_data(data)
    else:
        logger.warning("未选中主分组或子分组，无法通过拖动添加文件")