#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Preset list view
"""

import os
import shutil
import time

from PySide2.QtCore import Qt, QPoint
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QMenu,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QLineEdit,
    QDialogButtonBox,
)

from ..setting import cfg
from .. import formatter as fmt
from .. import regex_pattern as rxp
from .. import validator as val
from ._common import BaseDialog, QVAL_FILENAME

QSS_LISTBOX = (
    "QListView {font-size: 16px;outline: none;}"
    "QListView::item {height: 28px;border-radius: 0;}"
    "QListView::item:selected {selection-color: #FFF;background: #F20;}"
)
QSS_TAGGED_ITEM = "font-size: 14px;color: #FFF;"
QSS_TAGGED_COLOR = (
    "margin: 4px 4px 4px 0px;background: #F20;border-radius: 3px;",  # LMU
    "margin: 4px 4px 4px 0px;background: #0AF;border-radius: 3px;",  # RF2
)


class PresetList(QWidget):
    """Preset list view"""

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.preset_list = []

        # Label
        self.label_loaded = QLabel("")

        # Button
        button_load = QPushButton("Load")
        button_load.clicked.connect(self.load_preset)

        button_refresh = QPushButton("Refresh")
        button_refresh.clicked.connect(self.refresh_list)

        button_create = QPushButton("New Preset")
        button_create.clicked.connect(self.open_create_preset)

        # Check box
        self.checkbox_autoload = QCheckBox("Auto Load Primary Preset")
        self.checkbox_autoload.setChecked(cfg.application["enable_auto_load_preset"])
        self.checkbox_autoload.toggled.connect(self.toggle_autoload)

        # List box
        self.listbox_preset = QListWidget(self)
        self.listbox_preset.setAlternatingRowColors(True)
        self.listbox_preset.setStyleSheet(QSS_LISTBOX)
        self.listbox_preset.itemDoubleClicked.connect(self.load_preset)
        self.refresh_list()
        self.listbox_preset.setCurrentRow(0)

        # Layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_loaded)
        layout_main.addWidget(self.listbox_preset)
        layout_main.addWidget(self.checkbox_autoload)
        layout_button.addWidget(button_load)
        layout_button.addWidget(button_refresh)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_create)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

        self.listbox_context_menu = self.set_context_menu()
        self.listbox_preset.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listbox_preset.customContextMenuRequested.connect(self.open_context_menu)

    def refresh_list(self):
        """Refresh preset list"""
        self.preset_list = cfg.preset_list
        self.listbox_preset.clear()

        for preset_name in self.preset_list:
            # Add preset name
            item = QListWidgetItem()
            item.setText(preset_name)
            self.listbox_preset.addItem(item)
            # Add primary preset tag
            label_item = PrimaryPresetTag(preset_name)
            self.listbox_preset.setItemWidget(item, label_item)

        self.label_loaded.setText(f"Loaded: <b>{cfg.filename.last_setting[:-5]}</b>")
        self.checkbox_autoload.setChecked(cfg.application["enable_auto_load_preset"])

    def load_preset(self):
        """Load selected preset"""
        selected_index = self.listbox_preset.currentRow()
        if selected_index >= 0:
            cfg.filename.setting = f"{self.preset_list[selected_index]}.json"
            self.master.reload_preset()
        else:
            QMessageBox.warning(
                self, "Error",
                "No preset selected.\nPlease select a preset to continue.")

    def open_create_preset(self):
        """Create new preset"""
        _dialog = CreatePreset(self, title="Create new default preset")
        _dialog.open()

    @staticmethod
    def toggle_autoload(checked):
        """Toggle auto load preset"""
        cfg.application["enable_auto_load_preset"] = checked
        cfg.save(filetype="config")

    def set_context_menu(self):
        """Set context menu"""
        menu = QMenu()
        menu.addAction("Set Primary for LMU")
        menu.addAction("Set Primary for RF2")
        menu.addSeparator()
        menu.addAction("Clear Primary Tag")
        menu.addSeparator()
        menu.addAction("Duplicate")
        menu.addAction("Rename")
        menu.addAction("Delete")
        return menu

    def open_context_menu(self, position: QPoint):
        """Open context menu"""
        if not self.listbox_preset.itemAt(position):
            return

        selected_action = self.listbox_context_menu.exec_(
            self.listbox_preset.mapToGlobal(position))
        if not selected_action:
            return

        selected_index = self.listbox_preset.currentRow()
        selected_preset_name = self.preset_list[selected_index]
        selected_filename = f"{selected_preset_name}.json"
        action = selected_action.text()

        # Set primary preset LMU
        if action == "Set Primary for LMU":
            cfg.primary_preset["LMU"] = selected_preset_name
            cfg.save(filetype="config")
            self.refresh_list()
        # Set primary preset RF2
        elif action == "Set Primary for RF2":
            cfg.primary_preset["RF2"] = selected_preset_name
            cfg.save(filetype="config")
            self.refresh_list()
        # Clear primary preset tag
        elif action == "Clear Primary Tag":
            tag_found = False
            for sim_name, primary_preset in cfg.primary_preset.items():
                if selected_preset_name == primary_preset:
                    cfg.primary_preset[sim_name] = ""
                    tag_found = True
            if tag_found:
                cfg.save(filetype="config")
                self.refresh_list()
        # Duplicate preset
        elif action == "Duplicate":
            _dialog = CreatePreset(
                self,
                title="Duplicate Preset",
                mode="duplicate",
                source_filename=selected_filename
            )
            _dialog.open()
        # Rename preset
        elif action == "Rename":
            _dialog = CreatePreset(
                self,
                title="Rename Preset",
                mode="rename",
                source_filename=selected_filename
            )
            _dialog.open()
        # Delete preset
        elif action == "Delete":
            msg_text = (
                "<font style='font-size: 15px;'><b>Are you sure you want to delete<br>"
                f"'{selected_filename}'"
                " permanently?</b></font><br><br>This cannot be undone!"
            )
            delete_msg = QMessageBox.question(
                self, "Delete Preset", msg_text,
                buttons=QMessageBox.Yes | QMessageBox.No,
                defaultButton=QMessageBox.No,
            )
            if delete_msg == QMessageBox.Yes:
                if os.path.exists(f"{cfg.path.settings}{selected_filename}"):
                    os.remove(f"{cfg.path.settings}{selected_filename}")
                self.refresh_list()


class CreatePreset(BaseDialog):
    """Create preset"""

    def __init__(self, master, title: str = "", mode: str = "", source_filename: str = ""):
        """Initialize create preset dialog setting

        Args:
            title: Dialog title string.
            mode: Edit mode, either "duplicate", "rename", or "" for new preset.
            source_filename: Source setting filename.
        """
        super().__init__(master)
        self.master = master
        self.edit_mode = mode
        self.source_filename = source_filename

        self.setWindowTitle(title)
        self.setFixedWidth(280)

        # Entry box
        self.preset_entry = QLineEdit()
        self.preset_entry.setMaxLength(40)
        self.preset_entry.setPlaceholderText("Enter a new preset name")
        self.preset_entry.setValidator(QVAL_FILENAME)

        # Button
        button_create = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        button_create.accepted.connect(self.creating)
        button_create.rejected.connect(self.reject)

        # Layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.preset_entry)
        layout_main.addWidget(button_create)
        self.setLayout(layout_main)

    def creating(self):
        """Creating new preset"""
        entered_filename = fmt.strip_filename_extension(self.preset_entry.text(), ".json")

        if val.allowed_filename(rxp.CFG_INVALID_FILENAME, entered_filename):
            self.__saving(cfg.path.settings, entered_filename, self.source_filename)
        else:
            QMessageBox.warning(self, "Error", "Invalid preset name.")

    def __saving(self, filepath: str, entered_filename: str, source_filename: str):
        """Saving new preset"""
        # Check existing preset
        temp_list = cfg.preset_list
        for preset in temp_list:
            if entered_filename.lower() == preset.lower():
                QMessageBox.warning(self, "Error", "Preset already exists.")
                return None
        # Duplicate preset
        if self.edit_mode == "duplicate":
            shutil.copy(
                f"{filepath}{source_filename}",
                f"{filepath}{entered_filename}.json"
            )
            self.master.refresh_list()
        # Rename preset
        elif self.edit_mode == "rename":
            os.rename(
                f"{filepath}{source_filename}",
                f"{filepath}{entered_filename}.json"
            )
            # Reload if renamed file was loaded
            if cfg.filename.setting == source_filename:
                cfg.filename.setting = f"{entered_filename}.json"
                self.master.master.reload_preset()
            else:
                self.master.refresh_list()
        # Create new preset
        else:
            cfg.filename.setting = f"{entered_filename}.json"
            cfg.create()
            cfg.save(0)  # save setting
            while cfg.is_saving:  # wait saving finish
                time.sleep(0.01)
            self.master.refresh_list()
        # Close window
        self.accept()
        return None


class PrimaryPresetTag(QWidget):
    """Primary preset tag"""

    def __init__(self, preset_name: str):
        super().__init__()
        layout_item = QHBoxLayout()
        layout_item.setContentsMargins(0,0,0,0)
        layout_item.setSpacing(0)
        layout_item.addStretch(stretch=1)

        for sim_name, primary_preset in cfg.primary_preset.items():
            if preset_name == primary_preset:
                label_sim_name = QLabel(sim_name)
                label_sim_name.setStyleSheet(QSS_TAGGED_COLOR[sim_name == "RF2"])
                layout_item.addWidget(label_sim_name)

        self.setStyleSheet(QSS_TAGGED_ITEM)
        self.setLayout(layout_item)
