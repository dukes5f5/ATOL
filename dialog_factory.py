# -*- coding: utf-8 -*-
"""
Created on Sat Nov 15 13:33:15 2025

@author: dukes
"""


# --------------------------------
# 2. dialog_factory.py
# --------------------------------
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication
from dialogs_registry import REGISTRY
from utils import resource_path


class DialogFactory:
    def __init__(self, style_path = None):
        self.style_path = resource_path(f"{style_path}")
        self._apply_global_styles()

    def _apply_global_styles(self):
        if self.style_path and os.path.exists(self.style_path):
            with open(self.style_path, "r") as f:
                qss = f.read()
                QApplication.instance().setStyleSheet(qss)

    def create_dialog(self, key, parent=None, params=None):
        if key not in REGISTRY:
            raise KeyError(f"Dialog '{key}' not registered.")

        ui_file, result_func, init_func = REGISTRY[key]

        class CallableDialog(QDialog):
            def __init__(self, parent=None, params=None):
                super().__init__(parent)
                uic.loadUi(ui_file, self)
                if init_func and params:
                    init_func(self, params)
                    
                # Auto-wire buttonBox if it exists
                if hasattr(self, "buttonBox"):
                    self.buttonBox.accepted.connect(self.accept)
                    self.buttonBox.rejected.connect(self.reject)
        
                if init_func and params:
                    init_func(self, params)

            def __call__(self):
                if self.exec_() == QDialog.Accepted:
                    if result_func:
                        return result_func(self)
                    return {}
                return None

        return CallableDialog(parent, params)
