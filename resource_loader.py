# -*- coding: utf-8 -*-
"""
ResourceLoader - Unified resource loader for ATOL application.
Adapted for ATOL's directory structure while following DEFAULT_UIs patterns.
"""

import sys
import logging
from pathlib import Path

# Configure logging globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


class ResourceLoader:
    """
    Unified resource loader for dev and frozen states.
    Anchors everything to project root or PyInstaller _MEIPASS.
    Maintains ATOL's directory structure constants.
    """

    def __init__(self):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            self.base_path = Path(sys._MEIPASS)
            logging.debug("ResourceLoader: Frozen mode; base_path set to _MEIPASS")
        else:
            # Development mode - ATOL structure
            self.base_path = Path(__file__).resolve().parent
            logging.debug("ResourceLoader: Dev mode; base_path set to script directory")

        # ATOL-specific directory structure
        # In dev mode, all files are at the same level as MAIN.py
        # Structure expected:
        # /base_path/
        #   ├── MAIN.py
        #   ├── MAIN.ui
        #   ├── style_dark.qss
        #   ├── *.png icons
        #   └── (other modules)

        self.resources_dir = self.base_path
        logging.info(f"ResourceLoader: resources directory -> {self.resources_dir}")

    def get(self, *parts: str) -> str:
        """
        Resolve a resource path under the resources directory.
        Logs a warning if the file does not exist.
        """
        path = self.resources_dir.joinpath(*parts)
        if not path.exists():
            logging.warning(f"ResourceLoader: Resource not found -> {path}")
        else:
            logging.debug(f"ResourceLoader: Resource resolved -> {path}")
        return str(path)

    def get_ui(self, filename: str) -> str:
        """Get UI file path - ATOL keeps UI files at base level."""
        return self.get(filename)

    def get_style(self, filename: str) -> str:
        """Get stylesheet file path - ATOL keeps QSS at base level."""
        return self.get(filename)

    def get_image(self, filename: str) -> str:
        """Get image file path - ATOL keeps images at base level."""
        return self.get(filename)

    def get_icon(self, filename: str) -> str:
        """Get icon file path - ATOL keeps icons at base level."""
        return self.get(filename)

    def require(self, *parts: str) -> str:
        """
        Like get(), but raises FileNotFoundError if the resource is missing.
        Useful when a resource is mandatory for startup.
        """
        path = Path(self.get(*parts))
        if not path.exists():
            raise FileNotFoundError(f"Required resource missing: {path}")
        return str(path)

    # ATOL-specific directory constants
    @property
    def here(self) -> Path:
        """Return the path to the current script (MAIN.py location)."""
        return self.base_path

    @property
    def python_dir(self) -> Path:
        """Legacy: parent of HERE for old structure compatibility."""
        return self.base_path.parent

    @property
    def code_dir(self) -> Path:
        """Legacy: CODE directory for old structure."""
        return self.base_path.parent.parent

    @property
    def repo_root(self) -> Path:
        """Legacy: Repository root for old structure."""
        return self.base_path.parent.parent.parent

    @property
    def data_dir(self) -> Path:
        """DATA directory path."""
        return self.repo_root / "DATA"

    @property
    def affif_dir(self) -> Path:
        """AFFIF directory path under DATA."""
        return self.data_dir / "AFFIF"

    @property
    def custom_dir(self) -> Path:
        """CUSTOM directory path for user CSV input."""
        return self.repo_root / "CUSTOM"

    @property
    def returns_dir(self) -> Path:
        """RETURNS directory path for outputs."""
        return self.repo_root / "RETURNS"

    @property
    def gui_dir(self) -> Path:
        """GUI directory path (legacy)."""
        return self.python_dir / "GUI"

    @property
    def icons_dir(self) -> Path:
        """ICONS directory path (legacy)."""
        return self.gui_dir / "ICONS"

    @property
    def qss_dir(self) -> Path:
        """QSS directory path (legacy)."""
        return self.gui_dir / "QSS"

    @property
    def wmm_dir(self) -> Path:
        """WMM2025COF directory path (legacy)."""
        return self.python_dir / "WMM2025COF"
