# -*- coding: utf-8 -*-
"""
StdoutConsole - Redirect stdout/stderr to a Qt text widget.
Adapted from DEFAULT_UIs for ATOL application.
"""

import sys
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QTextCursor


class _TextEditStream(QObject):
    """
    Internal stream class that writes to a Qt text widget.
    Supports optional color override for error streams.
    """

    def __init__(self, text_edit, override_color=None):
        super().__init__()
        self.text_edit = text_edit
        self.override_color = override_color

    def write(self, text):
        """Write text to the text widget."""
        if not text.strip():
            return
        clean = text.strip()
        try:
            cursor = self.text_edit.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText(clean + "\n")
            self.text_edit.setTextCursor(cursor)
            self.text_edit.ensureCursorVisible()

            if self.override_color:
                self.text_edit.setStyleSheet(f"color: {self.override_color};")
        except Exception:
            # Fallback to real stdout if widget write fails
            sys.__stdout__.write(text)

    def flush(self):
        """Flush the stream (no-op for Qt widget)."""
        pass


class StdoutConsole:
    """
    Console redirector that captures stdout and stderr to a Qt text widget.
    
    Usage:
        self.console = StdoutConsole(self.textWidget)
        # ... use print() normally ...
        self.console.restore()  # on cleanup
    """

    def __init__(self, text_edit_widget):
        """
        Initialize the console redirector.
        
        Args:
            text_edit_widget: A Qt text widget (QPlainTextEdit, QTextEdit, etc.)
        """
        self.text_edit = text_edit_widget
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        self.stdout_stream = _TextEditStream(self.text_edit)
        self.stderr_stream = _TextEditStream(self.text_edit, override_color="#FF5555")

        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

    def restore(self):
        """Restore original stdout and stderr streams."""
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - restore streams."""
        self.restore()
        return False
