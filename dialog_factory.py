# -*- coding: utf-8 -*-
"""
DialogFactory - Dialog creation and management for ATOL application.
Provides a factory pattern for creating dialogs with UI files.
"""

import os
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication

from dialogs_registry import REGISTRY
from resource_loader import ResourceLoader


class DialogFactory:
    """
    Factory for creating dialogs from registered UI files.
    Supports global stylesheet application and parameterized initialization.
    """

    def __init__(self, style_path=None):
        """
        Initialize the dialog factory.
        
        Args:
            style_path: Optional path to a QSS stylesheet file.
        """
        self.loader = ResourceLoader()

        # Resolve style path using loader
        if style_path:
            self.style_path = self.loader.get_style(style_path)
        else:
            self.style_path = None

        self._apply_global_styles()

    def _apply_global_styles(self):
        """Apply global stylesheet to the application."""
        if self.style_path and os.path.exists(self.style_path):
            with open(self.style_path, "r") as f:
                qss = f.read()
                app = QApplication.instance()
                if app:
                    app.setStyleSheet(qss)

    def _resolve_ui_path(self, ui_file: str) -> str:
        """
        Resolve UI file path.
        
        Args:
            ui_file: UI filename or absolute path.
            
        Returns:
            Resolved path string.
        """
        if os.path.isabs(ui_file):
            return ui_file
        return self.loader.get_ui(ui_file)

    def create_dialog(self, key, parent=None, params=None):
        """
        Create a dialog instance from the registry.
        
        Args:
            key: Registry key for the dialog.
            parent: Parent widget for the dialog.
            params: Optional parameters to pass to the dialog initializer.
            
        Returns:
            A callable dialog instance.
        """
        if key not in REGISTRY:
            raise KeyError(f"Dialog '{key}' not registered.")

        ui_file, result_func, init_func = REGISTRY[key]
        ui_path = self._resolve_ui_path(ui_file)

        class CallableDialog(QDialog):
            def __init__(self, parent=None, params=None):
                super().__init__(parent)
                uic.loadUi(ui_path, self)

                if init_func and params:
                    init_func(self, params)

                # Auto-wire buttonBox if it exists
                if hasattr(self, "buttonBox"):
                    self.buttonBox.accepted.connect(self.accept)
                    self.buttonBox.rejected.connect(self.reject)

            def __call__(self):
                if self.exec_() == QDialog.Accepted:
                    return result_func(self) if result_func else {}
                return None

        return CallableDialog(parent, params)
