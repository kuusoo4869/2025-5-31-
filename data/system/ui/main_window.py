import sys
import os
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QListWidget, QFileDialog
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from data.system.log.log import logger
from data.system.tool.data_persistence import load_data, save_data
from data.system.tool.group_management import add_main_group, add_sub_group
from data.system.tool.file_management import add_files, handle_file_drop
from data.system.tool.config_management import load_config, save_config

class HoverListWidget(QListWidget):
    """
    自定义列表控件，用于处理鼠标悬停事件
    当鼠标悬停在列表项上时，自动选择该项
    """
    hovered = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        鼠标移动事件，处理鼠标悬停选择
        """
        index = self.indexAt(event.pos())
        if index.isValid():
            self.setCurrentRow(index.row())
            self.hovered.emit(index.row())
        super().mouseMoveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config  # 接收传入的配置字典
        """
        初始化主窗口
        """
        super().__init__()  # 确保在初始化逻辑开始时调用父类的 __init__ 方法
        try:
            logger.info("开始初始化主窗口")
            self.data = load_data()
            self.config = load_config()
            # 设置最小大小
            self.setMinimumSize(300, 300)
            # 初始化调整大小相关属性
            self.resizing = False
            self.resize_direction = None
            self.mouse_press_pos = None
            self.original_size = None
            self.original_pos = None
            self.init_ui()
            self.load_groups_to_ui()
            logger.info("主窗口初始化完成")
        except Exception as e:
            logger.error(f"主窗口初始化失败: {e}")
        
        # 连接主分组列表和子分组列表的选择变化信号
        # 初始化完成后再连接信号
        self.main_group_list.currentRowChanged.connect(self.on_main_group_changed)
        self.sub_group_list.currentRowChanged.connect(self.on_sub_group_changed)

    def init_ui(self):
        """
        初始化用户界面
        """
        # 设置窗口属性
        self.setWindowTitle("空想")
        # 删除下面这行代码
        # self.setFixedSize(500, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 创建主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 第一排控件
        first_row_widget = QWidget()
        first_row_layout = QHBoxLayout()
        first_row_widget.setLayout(first_row_layout)

        # 子控件1：设置按钮
        self.settings_button = QPushButton("设置")
        self.settings_button.clicked.connect(self.show_settings_window)
        first_row_layout.addWidget(self.settings_button, 1)
        logger.info("设置按钮已创建")

        # 子控件2：主分组列表
        self.main_group_list = HoverListWidget()
        self.main_group_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.main_group_list.customContextMenuRequested.connect(self.show_main_group_context_menu)
        # 设置尺寸策略为横向扩展
        from PyQt5.QtWidgets import QSizePolicy
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(8)
        size_policy.setVerticalStretch(0)
        # 设置固定高度
        fixed_height = 30  # 可根据实际需求调整高度
        self.main_group_list.setSizePolicy(size_policy)
        self.main_group_list.setFixedHeight(fixed_height)
        # 设置列表为横向滚动
        self.main_group_list.setFlow(QListWidget.LeftToRight)
        self.main_group_list.setWrapping(True)
        self.main_group_list.setResizeMode(QListWidget.Adjust)
        first_row_layout.addWidget(self.main_group_list, 8)
        logger.info("主分组列表已创建")

        # 子控件3：最小化、最大化、关闭按钮
        self.minimize_button = QPushButton("—")
        self.maximize_button = QPushButton("□")
        self.close_button = QPushButton("×")
        self.minimize_button.clicked.connect(self.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.close_button.clicked.connect(self.close)

        # 设置按钮固定宽度
        button_width = 30  # 可根据实际需求调整宽度
        self.minimize_button.setFixedWidth(button_width)
        self.maximize_button.setFixedWidth(button_width)
        self.close_button.setFixedWidth(button_width)

        first_row_layout.addWidget(self.minimize_button, 1)
        first_row_layout.addWidget(self.maximize_button, 1)
        first_row_layout.addWidget(self.close_button, 1)
        logger.info("窗口控制按钮已创建")

        # 第二排控件
        second_row_widget = QWidget()
        second_row_layout = QHBoxLayout()
        second_row_widget.setLayout(second_row_layout)

        # 子控件1：子分组列表
        self.sub_group_list = HoverListWidget()
        self.sub_group_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sub_group_list.customContextMenuRequested.connect(self.show_sub_group_context_menu)
        
        # 设置可水平扩展的尺寸策略
        sub_group_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 从配置获取子分组默认比例（当前20%）
        sub_group_default_ratio = self.config.get('sub_group_ratio', 20)
        # 从配置获取子分组比例（默认20%）
        sub_group_ratio = self.config.get('sub_group_ratio', 20)
        sub_group_size_policy.setHorizontalStretch(sub_group_ratio)  # 使用配置值设置拉伸因子
        self.sub_group_list.setSizePolicy(sub_group_size_policy)
        
        # 启用水平调整大小
        self.sub_group_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sub_group_list.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        
        # 设置分隔条可拖动
        from PyQt5.QtWidgets import QSplitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 强制设置分割条为可见
        self.splitter.setOpaqueResize(True)
        self.splitter.setChildrenCollapsible(False)
        
        self.splitter.addWidget(self.sub_group_list)
        
        # 设置分割条样式
        self.splitter.setHandleWidth(8)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #555;
                border: 1px solid #333;
                margin: 2px;
                width: 8px;
                height: 100%;
            }
            QSplitter::handle:hover {
                background-color: #777;
            }
        """)
        
        # 强制刷新布局
        self.splitter.updateGeometry()
        
        second_row_layout.addWidget(self.splitter, 2)  # 设置拉伸因子为4
        logger.info("子分组列表已创建，设置为可水平扩展并添加可拖动分隔条")

        # 子控件2：文件列表
        self.file_list = HoverListWidget()
        
        # 设置可水平扩展的尺寸策略
        file_list_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 从配置获取文件列表默认比例（当前80%）
        file_list_default_ratio = 100 - self.config.get('sub_group_ratio', 20)
        # 根据配置的子分组比例计算文件列表比例
        sub_group_ratio = self.config.get('sub_group_ratio', 20)
        file_list_ratio = 100 - sub_group_ratio
        file_list_size_policy.setHorizontalStretch(file_list_ratio)  # 使用计算值设置拉伸因子
        self.file_list.setSizePolicy(file_list_size_policy)
        
        # 启用水平调整大小
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.file_list.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        
        # 添加到分隔条
        self.splitter.addWidget(self.file_list)
        self.splitter.setStretchFactor(0, 4)  # 子分组列表拉伸因子
        self.splitter.setStretchFactor(1, 6)  # 文件列表拉伸因子
        logger.info("文件列表已创建，设置为可水平扩展并添加到分隔条")
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_file_context_menu)
        self.file_list.setAcceptDrops(True)
        self.file_list.doubleClicked.connect(self.open_file)
        self.file_list.dragEnterEvent = self.file_list_dragEnterEvent
        self.file_list.dragMoveEvent = self.file_list_dragMoveEvent
        self.file_list.dropEvent = self.file_list_dropEvent
        
        # 设置可水平扩展的尺寸策略
        file_list_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        file_list_size_policy.setHorizontalStretch(6)  # 默认占60%宽度
        self.file_list.setSizePolicy(file_list_size_policy)
        
        # 启用水平调整大小
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.file_list.setSizeAdjustPolicy(QListWidget.AdjustToContents)
        
        second_row_layout.addWidget(self.file_list, 6)  # 设置拉伸因子为6
        logger.info("文件列表已创建，设置为可水平扩展")

        main_layout.addWidget(first_row_widget, 1)
        main_layout.addWidget(second_row_widget, 9)

        # 实现窗口拖动功能
        self.draggable = False
        self.offset = None

    def show_settings_window(self):
        # 初始化设置窗口
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QVBoxLayout, QPushButton
        from PyQt5.QtCore import Qt

        class SettingsWindow(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("设置")
                self.setWindowModality(Qt.ApplicationModal)
                self.layout = QVBoxLayout()

                # 主窗口尺寸输入
                self.main_width_input = QLineEdit(str(self.parent().width()))
                self.main_height_input = QLineEdit(str(self.parent().height()))

                # 比例输入
                self.sub_group_ratio_input = QLineEdit("20")

                # 表单布局
                form_layout = QFormLayout()

                # 添加提示文本
                from PyQt5.QtWidgets import QLabel
                hint_label = QLabel('可点击窗口边缘拖动大小')
                form_layout.addRow(hint_label)
                form_layout.addRow("主窗口宽度 (最小300):", self.main_width_input)
                form_layout.addRow("主窗口高度 (最小300):", self.main_height_input)
                # form_layout.addRow("子分组列表宽度比例:", self.sub_group_ratio_input)

                # 保存按钮
                save_btn = QPushButton("保存并应用")
                save_btn.clicked.connect(self.save_settings)
                
                # 作者按钮
                author_btn = QPushButton("作者")
                author_btn.clicked.connect(self.show_author_info)

                self.layout.addLayout(form_layout)
                self.layout.addWidget(save_btn)
                self.layout.addWidget(author_btn)
                self.setLayout(self.layout)
                
            def show_author_info(self):
                """
                显示作者信息对话框
                """
                from PyQt5.QtWidgets import QMessageBox
                from PyQt5.QtCore import QUrl
                from PyQt5.QtGui import QDesktopServices
                
                msg_box = QMessageBox()
                msg_box.setWindowTitle("作者信息")
                msg_box.setTextFormat(Qt.RichText)
                msg_box.setText("空想 <a href=\"https://kuusoo.me/\">https://kuusoo.me/</a>")
                msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
                msg_box.exec_()
                
                # 仅显示链接，不自动打开
                 # 用户可自行点击对话框中的链接

            def save_settings(self):
                # 实时更新主窗口尺寸
                try:
                    # 验证主窗口尺寸输入为数字
                    try:
                        new_width = int(self.main_width_input.text())
                        new_height = int(self.main_height_input.text())
                    except ValueError:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, '输入错误', '主窗口尺寸必须为数字', QMessageBox.Ok)
                        return
                    self.parent().resize(new_width, new_height)

                    # 验证子分组比例输入为数字
                    try:
                        sub_ratio = int(self.sub_group_ratio_input.text())
                    except ValueError:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, '输入错误', '子分组比例必须为数字', QMessageBox.Ok)
                        return
                    file_ratio = 100 - sub_ratio
                    # 保存子分组比例到配置
                    # 保存子分组比例到配置并持久化
                    self.parent().config['sub_group_ratio'] = sub_ratio
                    # 写入配置文件（字典方式）
                    self.parent().config['sub_group_ratio'] = sub_ratio
                    logger.info(f"保存比例设置：子分组比例{sub_ratio}%，文件列表比例{file_ratio}%")
                    if sub_ratio + file_ratio != 100:
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, '输入错误', '子分组列表与文件列表的宽度比例和必须为100%', QMessageBox.Ok)
                        return

                    # 检查 splitter 属性是否存在
                    if hasattr(self.parent(), 'splitter'):
                        # 更新分隔条比例
                        self.parent().splitter.setStretchFactor(0, sub_ratio)
                        self.parent().splitter.setStretchFactor(1, file_ratio)

                        # 强制更新布局以获取最新宽度
                        self.parent().splitter.update()
                        # 获取分隔条实际可用宽度（扣除边距）
                        total_width = self.parent().splitter.width() - 10  # 减去10像素边距
                        # 验证比例范围
                        if not (0 <= sub_ratio <= 100):
                            from PyQt5.QtWidgets import QMessageBox
                            QMessageBox.warning(self, '输入错误', '子分组比例必须在0-100之间', QMessageBox.Ok)
                            return
                        # 计算并设置尺寸
                        sub_width = int(total_width * sub_ratio / 100)
                        file_width = total_width - sub_width  # 确保总宽度准确
                        self.parent().splitter.setSizes([sub_width, file_width])
                    else:
                        logger.error('MainWindow 实例中不存在 splitter 属性')
                        from PyQt5.QtWidgets import QMessageBox
                        QMessageBox.warning(self, '设置失败', '无法找到分隔条控件，请检查程序配置。', QMessageBox.Ok)
                        return
                    logger.info(f"比例设置保存完成：子分组宽度{sub_width}px，文件列表宽度{file_width}px")

                    logger.info(f"设置更新：主窗口尺寸{new_width}x{new_height}，比例{sub_ratio}:{file_ratio}")
                    self.accept()
                except Exception as e:
                    logger.error(f"设置保存失败：{str(e)}")

        # 显示设置窗口
        self.settings_window = SettingsWindow(self)
        # 打印当前设置变量
        current_width = self.width()
        current_height = self.height()
        default_sub_ratio = self.settings_window.sub_group_ratio_input.text()
        logger.info(f"打开设置窗口，当前主窗口尺寸：{current_width}x{current_height}，子分组默认比例：{default_sub_ratio}%")
        self.settings_window.show()

    def load_groups_to_ui(self):
        """
        将从文件加载的数据显示到 UI 上
        """
        self.main_group_list.clear()
        for main_group in self.data["mainGroups"]:
            self.main_group_list.addItem(main_group["name"])
        
        # 当存在主分组时，触发主分组变化事件以更新子分组和文件列表
        if self.data["mainGroups"]:
            self.on_main_group_changed(0)

    def on_main_group_changed(self, index):
        """
        主分组选择变化时，更新子分组列表和清空文件列表，并记录日志
        """
        self.sub_group_list.clear()
        self.file_list.clear()
        logger.info(f"主分组切换到索引 {index}，开始更新子分组列表和清空文件列表")
        if index >= 0 and index < len(self.data["mainGroups"]):
            main_group = self.data["mainGroups"][index]
            for sub_group in main_group["subGroups"]:
                self.sub_group_list.addItem(sub_group["name"])
            logger.info(f"主分组索引 {index} 对应的子分组列表更新完成")
            
            # 当存在子分组时，触发子分组变化事件以更新文件列表
            if main_group["subGroups"]:
                self.on_sub_group_changed(0)
        else:
            logger.info("未选中主分组，子分组列表和文件列表保持为空")
    
    def on_sub_group_changed(self, index):
        """
        子分组选择变化时，更新文件列表，并记录日志。
        若成功获取到子分组的文件列表，将文件列表数据打印到日志中。
        """
        self.file_list.clear()
        selected_main_index = self.main_group_list.currentRow()
        logger.info(f"子分组切换到索引 {index}，主分组索引为 {selected_main_index}，开始更新文件列表")
        if selected_main_index >= 0 and index >= 0:
            main_group = self.data["mainGroups"][selected_main_index]
            if main_group["subGroups"] and index < len(main_group["subGroups"]):
                sub_group = main_group["subGroups"][index]
                file_list_data = []
                for file in sub_group["files"]:
                    self.file_list.addItem(file["name"])
                    file_list_data.append(file)
                logger.info(f"主分组索引 {selected_main_index}，子分组索引 {index} 对应的文件列表更新完成，文件列表数据: {file_list_data}")
        else:
            logger.info("未选中有效的主分组或子分组，文件列表保持为空")

    def show_main_group_context_menu(self, pos):
        """
        显示主分组列表的右键菜单，提供添加主分组和删除主分组的功能
        """
        from PyQt5.QtWidgets import QMenu, QMessageBox
        logger.info("用户在主分组列表右键点击，显示右键菜单")
        menu = QMenu(self)
        add_main_group_action = menu.addAction("添加主分组")
        delete_main_group_action = menu.addAction("删除主分组")
        action = menu.exec_(self.main_group_list.mapToGlobal(pos))
    
        selected_index = self.main_group_list.currentRow()
        if action == add_main_group_action:
            add_main_group(self.data, self.main_group_list)
        elif action == delete_main_group_action and selected_index >= 0:
            reply = QMessageBox.question(self, '确认删除', '确定要删除这个主分组吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.data["mainGroups"][selected_index]
                save_data(self.data)
                self.main_group_list.takeItem(selected_index)
                self.sub_group_list.clear()
                self.file_list.clear()
                logger.info(f"已删除主分组，索引: {selected_index}")
    
                # 检查是否还有剩余的主分组
                if len(self.data["mainGroups"]) > 0:
                    self.on_main_group_changed(0)
    
    def show_sub_group_context_menu(self, pos):
        """
        显示子分组列表的右键菜单，提供添加子分组和删除子分组的功能
        """
        from PyQt5.QtWidgets import QMenu, QMessageBox
        logger.info("用户在子分组列表右键点击，显示右键菜单")
        menu = QMenu(self)
        add_sub_group_action = menu.addAction("添加子分组")
        delete_sub_group_action = menu.addAction("删除子分组")
        action = menu.exec_(self.sub_group_list.mapToGlobal(pos))
    
        selected_main_index = self.main_group_list.currentRow()
        selected_sub_index = self.sub_group_list.currentRow()
        if selected_main_index >= 0:
            if action == add_sub_group_action:
                add_sub_group(self.data, self.main_group_list, self.sub_group_list, selected_main_index)
            elif action == delete_sub_group_action and selected_sub_index >= 0:
                reply = QMessageBox.question(self, '确认删除', '确定要删除这个子分组吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    main_group = self.data["mainGroups"][selected_main_index]
                    del main_group["subGroups"][selected_sub_index]
                    save_data(self.data)
                    self.sub_group_list.takeItem(selected_sub_index)
                    self.file_list.clear()
                    logger.info(f"已删除子分组，主分组索引: {selected_main_index}，子分组索引: {selected_sub_index}")

                # 检查是否还有剩余的子分组
                if len(main_group["subGroups"]) > 0:
                    self.on_sub_group_changed(0)

    def show_file_context_menu(self, pos):
        """
        显示文件列表的右键菜单，提供添加文件和删除文件的功能
        """
        from PyQt5.QtWidgets import QMenu, QMessageBox
        logger.info("用户在文件列表右键点击，显示右键菜单")
        menu = QMenu(self)
        add_file_action = menu.addAction("添加文件")
        delete_file_action = menu.addAction("删除文件")
        action = menu.exec_(self.file_list.mapToGlobal(pos))
    
        selected_main_index = self.main_group_list.currentRow()
        selected_sub_index = self.sub_group_list.currentRow()
        if selected_main_index < 0:
            QMessageBox.warning(self, "错误", "请先选择一个主分组")
            logger.warning("未选中主分组，无法添加或删除文件")
            return
        if selected_sub_index < 0:
            QMessageBox.warning(self, "错误", "请先选择一个子分组")
            logger.warning("未选中子分组，无法添加或删除文件")
            return
    
        selected_file_index = self.file_list.currentRow()
        if action == add_file_action:
            add_files(self.data, self.main_group_list, self.sub_group_list, self.file_list, selected_main_index, selected_sub_index)
        elif action == delete_file_action and selected_file_index >= 0:
            reply = QMessageBox.question(self, '确认删除', '确定要删除这个文件吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                main_group = self.data["mainGroups"][selected_main_index]
                sub_group = main_group["subGroups"][selected_sub_index]
                file_name = self.file_list.item(selected_file_index).text()
                for i, file in enumerate(sub_group["files"]):
                    if file["name"] == file_name:
                        del sub_group["files"][i]
                        break
                save_data(self.data)
                self.file_list.takeItem(selected_file_index)
                logger.info(f"已删除文件: {file_name}，主分组索引: {selected_main_index}，子分组索引: {selected_sub_index}")

    def file_list_dropEvent(self, event: QDropEvent):
        """
        处理文件列表的放下事件，将拖入的文件添加到列表中
        """
        handle_file_drop(self.data, self.main_group_list, self.sub_group_list, self.file_list, event)

    def open_file(self, index):
        """
        用原生程序打开选中的文件
        """
        try:
            selected_main_index = self.main_group_list.currentRow()
            selected_sub_index = self.sub_group_list.currentRow()
            if selected_main_index >= 0 and selected_sub_index >= 0:
                main_group = self.data["mainGroups"][selected_main_index]
                if main_group["subGroups"] and selected_sub_index < len(main_group["subGroups"]):
                    sub_group = main_group["subGroups"][selected_sub_index]
                    item = self.file_list.item(index.row())
                    file_name = item.text()
                    for file in sub_group["files"]:
                        if file["name"] == file_name:
                            file_path = file["path"]  # 使用保存的完整路径
                            os.startfile(file_path)
                            logger.info(f"用原生程序打开文件: {file_name}")
                            break
        except FileNotFoundError:
            logger.error(f"文件 {file_name} 未找到")
        except Exception as e:
            logger.error(f"打开文件 {file_name} 时发生未知错误: {e}")

    def toggle_maximize(self):
        """
        切换窗口最大化状态
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        logger.info("用户点击最大化按钮，切换窗口状态")

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件，处理窗口拖动、调整大小、更新鼠标指针样式
        参数:
            event: 鼠标事件对象
        """
        pos = event.pos()
        logger.debug(f"鼠标移动 - 屏幕坐标: ({event.globalPos().x()}, {event.globalPos().y()}), "
                    f"窗口坐标: ({pos.x()}, {pos.y()}), "
                    f"窗口状态: [拖动: {self.draggable}, 调整: {self.resizing}]")
        
        # 更新鼠标光标样式
        self.update_cursor(pos)
        
        # 处理窗口拖动
        if self.draggable:
            new_pos = self.pos() + event.globalPos() - self.mouse_press_pos
            self.move(new_pos)
            self.mouse_press_pos = event.globalPos()
            logger.info(f"窗口拖动中 - 新位置: ({new_pos.x()}, {new_pos.y()}), "
                        f"原始位置: ({self.original_pos.x()}, {self.original_pos.y()})")
            return
            
        # 处理窗口调整大小
        if self.resizing:
            delta = event.globalPos() - self.mouse_press_pos
            new_width = self.original_size.width()
            new_height = self.original_size.height()
            new_x = self.original_pos.x()
            new_y = self.original_pos.y()
    
            if self.resize_direction in ['left', 'left_top', 'left_bottom']:
                new_width -= delta.x()
                new_x += delta.x()
            elif self.resize_direction in ['right', 'right_top', 'right_bottom']:
                new_width += delta.x()
    
            if self.resize_direction in ['top', 'left_top', 'right_top']:
                new_height -= delta.y()
                new_y += delta.y()
            elif self.resize_direction in ['bottom', 'left_bottom', 'right_bottom']:
                new_height += delta.y()
    
            self.setGeometry(new_x, new_y, new_width, new_height)
            logger.info(f"窗口调整中 - 方向: {self.resize_direction}, "
                        f"原始大小: {self.original_size.width()}x{self.original_size.height()}, "
                        f"新大小: {new_width}x{new_height}, "
                        f"偏移量: ({delta.x()}, {delta.y()})")
            return
        
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """
        鼠标按下事件，处理窗口拖动和调整大小，并记录日志
        """
        if event.button() == Qt.LeftButton:
            logger.info("鼠标左键按下")
            self.mouse_press_pos = event.globalPos()
            self.original_size = self.size()
            self.original_pos = self.pos()
            if self.is_resize_area(event.pos()):
                self.resizing = True
                self.resize_direction = self.get_resize_direction(event.pos())
                logger.info(f"开始调整窗口大小，方向: {self.resize_direction}")
            else:
                self.draggable = True
                self.offset = event.pos()
                logger.info("开始拖动窗口")
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件，处理窗口拖动和调整大小
        """
        if event.button() == Qt.LeftButton:
            if self.resizing:
                self.resizing = False
                self.resize_direction = None
                logger.info("窗口大小调整结束")
            else:
                self.draggable = False
                self.offset = None
                logger.info("窗口拖动结束")
        
        # 鼠标释放时强制恢复默认光标样式
        self.setCursor(Qt.ArrowCursor)
        logger.info("鼠标释放，强制恢复默认光标样式")
        super().mouseReleaseEvent(event)
    
    def update_cursor(self, pos):
        """
        更新鼠标光标样式
        参数:
            pos: 鼠标当前位置
        """
        # 实时更新光标样式，不受拖动/调整状态限制
        if self.is_resize_area(pos):
            direction = self.get_resize_direction(pos)
            cursor_map = {
                'left': Qt.SizeHorCursor,
                'right': Qt.SizeHorCursor,
                'top': Qt.SizeVerCursor,
                'bottom': Qt.SizeVerCursor,
                'left_top': Qt.SizeFDiagCursor,
                'right_bottom': Qt.SizeFDiagCursor,
                'right_top': Qt.SizeBDiagCursor,
                'left_bottom': Qt.SizeBDiagCursor
            }
            self.setCursor(cursor_map.get(direction, Qt.ArrowCursor))
            logger.debug(f"光标更新为: {direction}")
            return
            
        # 默认光标
        self.setCursor(Qt.ArrowCursor)

    def is_resize_area(self, pos):
        """
        检查鼠标是否在可调整大小的区域内
        """
        # 动态计算边缘检测区域，基于窗口大小比例
        border = max(10, min(20, int(self.width() * 0.02), int(self.height() * 0.02)))
        corner_size = border * 1.5  # 对角线区域比边缘稍大
        
        rect = self.rect()
        
        # 精确边缘检测
        left_edge = pos.x() <= border
        right_edge = pos.x() >= rect.width() - border
        top_edge = pos.y() <= border
        bottom_edge = pos.y() >= rect.height() - border
        
        # 精确对角线检测
        in_corner = (
            (left_edge and top_edge) or
            (left_edge and bottom_edge) or
            (right_edge and top_edge) or
            (right_edge and bottom_edge)
        )
        
        # 记录详细检测信息
        logger.debug(f"边缘检测 - 位置: {pos}, 窗口大小: {rect.width()}x{rect.height()}, "
                    f"border: {border}, 边缘: L:{left_edge} R:{right_edge} T:{top_edge} B:{bottom_edge}")
        
        return left_edge or right_edge or top_edge or bottom_edge

    def get_resize_direction(self, pos):
        """
        获取鼠标所在的调整大小方向
        """
        # 动态计算边缘检测区域（与is_resize_area保持一致）
        border = max(10, min(20, int(self.width() * 0.02), int(self.height() * 0.02)))
        corner_size = border * 1.5  # 对角线区域比边缘稍大
        rect = self.rect()
        
        # 优化边缘检测逻辑
        is_left = pos.x() <= border
        is_right = pos.x() >= rect.width() - border
        is_top = pos.y() <= border
        is_bottom = pos.y() >= rect.height() - border
        
        # 添加对角线区域增强检测
        in_left_corner = pos.x() <= corner_size
        in_right_corner = pos.x() >= rect.width() - corner_size
        in_top_corner = pos.y() <= corner_size
        in_bottom_corner = pos.y() >= rect.height() - corner_size

        if is_left and is_top:
            return 'left_top'
        elif is_left and is_bottom:
            return 'left_bottom'
        elif is_right and is_top:
            return 'right_top'
        elif is_right and is_bottom:
            return 'right_bottom'
        elif is_left:
            return 'left'
        elif is_right:
            return 'right'
        elif is_top:
            return 'top'
        elif is_bottom:
            return 'bottom'

    def file_list_dragEnterEvent(self, event: QDragEnterEvent):
        """
        处理文件列表的拖入事件，始终接受事件，后续在 dragMoveEvent 中处理禁止情况
        """
        event.accept()
        selected_main_index = self.main_group_list.currentRow()
        selected_sub_index = self.sub_group_list.currentRow()
        logger.info(f"文件拖入事件触发，主分组索引: {selected_main_index}，子分组索引: {selected_sub_index}")

    def file_list_dragMoveEvent(self, event):
        """
        处理文件列表的拖动移动事件，在不满足条件时忽略事件以显示禁止图标
        """
        selected_main_index = self.main_group_list.currentRow()
        selected_sub_index = self.sub_group_list.currentRow()
        if selected_main_index < 0 or selected_sub_index < 0:
            event.ignore()
            return
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if not os.path.isfile(file_path):
                    event.ignore()
                    return
        event.accept()

    def file_list_dropEvent(self, event: QDropEvent):
        """
        处理文件列表的放下事件，将拖入的文件添加到列表中
        """
        from PyQt5.QtWidgets import QMessageBox
        selected_main_index = self.main_group_list.currentRow()
        selected_sub_index = self.sub_group_list.currentRow()
        logger.info(f"开始处理文件放下事件，当前主分组索引: {selected_main_index}，子分组索引: {selected_sub_index}")
        if selected_main_index >= 0 and selected_sub_index >= 0:
            main_group = self.data["mainGroups"][selected_main_index]
            if main_group["subGroups"] and selected_sub_index < len(main_group["subGroups"]):
                sub_group = main_group["subGroups"][selected_sub_index]
                existing_file_names = [file["name"] for file in sub_group["files"]]
                new_id = 1
                if sub_group["files"]:
                    try:
                        new_id = max(file["id"] for file in sub_group["files"]) + 1
                    except ValueError:
                        logger.error("计算新文件 ID 时出错，子分组文件列表可能为空")
                added_files = False
                for url in event.mimeData().urls():
                    file_path = url.toLocalFile()
                    if os.path.isfile(file_path):
                        file_name = os.path.basename(file_path)
                        # 数据验证：检查文件名称是否重复
                        if file_name in existing_file_names:
                            QMessageBox.warning(self, "错误", f"文件 {file_name} 已存在，请选择其他文件。")
                            continue
                        try:
                            file_size = os.path.getsize(file_path)
                        except FileNotFoundError:
                            logger.error(f"获取文件 {file_name} 大小时出错，文件可能已被移动或删除")
                            continue
                        new_file = {
                            "id": new_id,
                            "name": file_name,
                            "size": f"{file_size}B",
                            "path": file_path
                        }
                        sub_group["files"].append(new_file)
                        new_id += 1
                        added_files = True
                        logger.info(f"通过拖动添加文件: {file_name}")
                        self.file_list.addItem(file_name)  # 确保文件添加到 UI 列表中
                if added_files:
                    try:
                        # 尝试保存数据
                        save_data(self.data)
                        logger.info("数据保存成功")
                        self.on_sub_group_changed(selected_sub_index)
                        # 添加成功添加的日志
                        logger.info("成功添加文件到列表，UI 已更新")
                    except Exception as e:
                        # 记录保存数据时的错误信息
                        logger.error(f"保存数据时出错: {e}")
                        QMessageBox.critical(self, "错误", f"保存数据时出错: {e}")
                        # 回滚添加的文件
                        sub_group["files"] = [file for file in sub_group["files"] if file["id"] < new_id - len([url for url in event.mimeData().urls() if os.path.isfile(url.toLocalFile())])]
                        logger.info("数据保存失败，已回滚添加的文件")
            else:
                logger.warning("未选中主分组或子分组，无法通过拖动添加文件")
        else:
            logger.warning("未选中主分组或子分组，无法通过拖动添加文件")
        event.acceptProposedAction()