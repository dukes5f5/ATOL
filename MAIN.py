"""
ATOL v3 Main Application - Modular Architecture

Major features:
- Modular architecture based on DEFAULT_UIs patterns
- ResourceLoader for unified resource path handling
- DialogFactory for dialog creation and management
- LicenseManager for license validation at startup
- StdoutConsole for stdout/stderr redirection to GUI
- Dynamic, robust path handling with ATOL directory structure constants
- Safer I/O with explicit error handling and user messages (QMessageBox)
- All heavy I/O/processing calls are wrapped in try/except for better UX

Usage:
- Run from the ATOL directory: python MAIN.py
"""

import sys
import os
import math
from pathlib import Path

import pandas as pd
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QHeaderView,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import (
    QStandardItemModel,
    QStandardItem,
    QBrush,
    QColor,
    QFont,
)
from PyQt5.QtCore import Qt

# Local imports - ATOL modules
from accdb_reader import read_accdb_tables
from simple_distance import distance
from runwaykml import makerunway_kml
from runwayxml import makerunway_xml

# Modular imports from DEFAULT_UIs architecture
from resource_loader import ResourceLoader
from dialog_factory import DialogFactory
from license_manager import LicenseManager
from stdout_console import StdoutConsole


# -------------------------
# Dynamic path resolution
# -------------------------
# ATOL directory structure constants
# File layout assumption:
# repo/
#   CODE/
#     PYTHON/   <-- this MAIN.py lives here
#       MAIN.py
#       MAIN.ui (or GUI/MAIN.ui)
#   DATA/
#     AFFIF/
#   CUSTOM/    <-- user CSV input at repo root
#   RETURNS/   <-- outputs at repo root

HERE = Path(__file__).resolve()
PYTHON_DIR = HERE.parent
CODE_DIR = PYTHON_DIR.parent
REPO_ROOT = CODE_DIR.parent

DATA_DIR = REPO_ROOT / "DATA"
AFFIF_DIR = DATA_DIR / "AFFIF"
CUSTOM_DIR = REPO_ROOT / "CUSTOM"
RETURNS_DIR = REPO_ROOT / "RETURNS"
GUI_DIR = PYTHON_DIR / "GUI"
ICONS_DIR = GUI_DIR / "ICONS"
QSS_DIR = GUI_DIR / "QSS"
WMM_DIR = PYTHON_DIR / "WMM2025COF"


# -------------------------
# Utility functions
# -------------------------
def get_accdb_file():
    """Return first .accdb in DATA/AFFIF, raise informative error if missing."""
    if not AFFIF_DIR.exists():
        raise FileNotFoundError(f"AFFIF directory not found: {AFFIF_DIR}")
    files = list(AFFIF_DIR.glob("*.accdb"))
    if not files:
        raise FileNotFoundError(f"No .accdb files found in {AFFIF_DIR}")
    return files[0]


def make_returns_path(icao: str) -> Path:
    """Return the directory path to store outputs for a given ICAO, creating it if needed."""
    icao = str(icao).strip().upper()
    if not is_valid_icao(icao):
        raise ValueError(f"Invalid ICAO value: {icao}")
    outdir = RETURNS_DIR / icao
    outdir.mkdir(parents=True, exist_ok=True)
    return outdir


def is_valid_icao(icao: str) -> bool:
    """Simple validation: 1-4 alphanumeric characters (not '-')"""
    if not icao:
        return False
    icao = icao.strip()
    if icao == "-":
        return False
    return 0 < len(icao) <= 4 and icao.isalnum()


# -------------------------
# License validation
# -------------------------
def validate_license():
    """
    Validate the application license at startup.
    Returns True if license is valid, False otherwise.
    """
    try:
        license_mgr = LicenseManager()
        if not license_mgr.check():
            print("❌ License expired, deleted, or invalid for this machine/key.")
            return False
        return True
    except FileNotFoundError as e:
        # userkey.txt is missing - allow app to run in unlicensed mode
        print(f"⚠️ License file not found: {e}. Running in demo mode.")
        return True
    except Exception as e:
        print(f"⚠️ License check failed: {e}. Running in demo mode.")
        return True


# -------------------------
# MainWindow implementation
# -------------------------
class MainWindow(QMainWindow):
    """
    Main application window for the ATOL v3 interface.
    Uses modular architecture with ResourceLoader, DialogFactory, and StdoutConsole.
    """

    # Column mapping between display names and dataframe columns
    DISPLAY_COLUMN_MAPPING = {"ICAO": "icao", "WAC#": "wac_innr", "NAME": "arpt_name"}

    def __init__(self):
        super().__init__()
        
        # Initialize ResourceLoader and DialogFactory
        self.loader = ResourceLoader()
        
        try:
            self.initialize_ui()
        except Exception as e:
            # If UI cannot be loaded we must abort
            QMessageBox.critical(None, "Startup Error", f"Failed to initialize UI: {e}")
            raise
        
        self.setup_initial_values()
        self.connect_signals()

    def initialize_ui(self):
        """Load the UI file, apply styles, and prepare widgets."""
        # Try MAIN.ui in current directory first, then fall back to GUI_DIR
        ui_path = self.loader.get_ui("MAIN.ui")
        if not Path(ui_path).is_file():
            ui_path = GUI_DIR / "MAIN.ui"
            if not ui_path.is_file():
                raise FileNotFoundError(f"UI file not found: {ui_path}")
            ui_path = str(ui_path)
        
        loadUi(ui_path, self)

        # Initialize DialogFactory with stylesheet
        style_path = self.loader.get_style("style_dark.qss")
        self.factory = DialogFactory(style_path=style_path)

        # Redirect stdout/stderr to the CMD window widget using StdoutConsole
        self.console = None
        try:
            if hasattr(self, "CMDwindow") and self.CMDwindow:
                self.console = StdoutConsole(self.CMDwindow)
        except Exception:
            # If CMDwindow not present or redirect fails, keep default stdout
            pass

        # Initial UI state
        self._setup_initial_ui_state()

        # Initialize combo boxes
        self.setup_combo_boxes()

    def _setup_initial_ui_state(self):
        """Configure initial visibility and text of UI elements."""
        try:
            self.AFFIF_DATA_ICON_label.hide()
            self.AFFIF_DATA_labelEdit.setText("")
            self.rwyModWidget.hide()
            self.rwymodtable.hide()
            self.Add_ICAO_QWidget.hide()
            self.Add_ICAO_button1.hide()
            self.CUSTOM_DATA_ICON_label.hide()
            self.CUSTOM_DATA_labelEdit.setText("")
        except Exception:
            # Some UI elements may be named differently in variants of the UI;
            # ignore missing widgets to allow partial compatibility.
            pass

    def setup_combo_boxes(self):
        """Populate initial combo box options and defaults."""
        try:
            self.AIRFIELD_OPERAND_comboBox.clear()
            self.AIRFIELD_OPERAND_comboBox.addItems([">", "<"])

            self.DATABASE_AIRFIELDS_comboBox.clear()
            # Display names visible to user (map to dataframe columns below)
            self.DATABASE_AIRFIELDS_comboBox.addItems(["ICAO", "WAC#", "NAME"])

            self.AIRFIELD_OPERAND__DISTANCE_lineEdit.setText("7999")
        except Exception:
            pass

    def setup_initial_values(self):
        """Read initial values from UI into attributes (non-validated)."""
        # Use .text() where available; catch if widget missing
        def tget(widget, default=""):
            try:
                return widget.text()
            except Exception:
                return default

        self.TD_Dist = tget(getattr(self, "TD_Dist_lineEdit", None), "")
        self.STP_Dist = tget(getattr(self, "STP_Dist_lineEdit", None), "")
        self.G_Slope = tget(getattr(self, "G_Slope_lineEdit", None), "")
        self.TP_alt = tget(getattr(self, "TP_Alt_lineEdit", None), "")  # In feet
        self.GA_spd = tget(getattr(self, "GA_Spd_lineEdit", None), "")

    def connect_signals(self):
        """Wire UI controls to handlers (safe: check widget existence)."""
        try:
            self.AFFIF_DATA_pushButton.clicked.connect(self.load_db)
            self.CUSTOM_DATA_pushButton.clicked.connect(self.load_custom)
            self.selectAllpushButton.clicked.connect(self.select_all_rows)
            self.PROCESS_SELECTED_pushButton.clicked.connect(self.collect_checked_rows)
            self.Add_ICAO_button1.clicked.connect(self.set_icao_from_input)
            self.Add_ICAO_lineEdit.textChanged.connect(self.on_icao_text_changed)
            self.Add_ICAO_button1.clicked.connect(self.rwyModWidget.show)

            self.DATABASE_AIRFIELDS_SEARCH_lineEdit.textChanged.connect(self.search_table)
            self.DATABASE_AIRFIELDS_comboBox.currentTextChanged.connect(
                lambda: self.search_table(self.DATABASE_AIRFIELDS_SEARCH_lineEdit.text())
            )

            self.AIRFIELD_OPERAND_comboBox.currentTextChanged.connect(self.refilter_table)
            self.AIRFIELD_OPERAND__DISTANCE_lineEdit.installEventFilter(self)

            self.setup_connections()
        except Exception:
            # If some widgets missing, skip connecting them to avoid crashes
            pass

    def setup_connections(self):
        """Additional signal hookups."""
        try:
            self.AIRFIELD_OPERAND_comboBox.currentIndexChanged.connect(self.populate_selected_columns)
            self.AIRFIELD_OPERAND__DISTANCE_lineEdit.returnPressed.connect(self.populate_selected_columns)
            self.AIRFIELD_OPERAND__DISTANCE_lineEdit.editingFinished.connect(self.populate_selected_columns)
            self.rwyModWidget_YES.clicked.connect(self.handle_rwyMod_yes)
            self.rwyModWidget_NO.clicked.connect(self.handle_rwyMod_no)
            self.rwymodtable_CONTINUE.clicked.connect(self.handle_rwymodtable)
        except Exception:
            pass

    # -------------------------
    # Data loading and processing
    # -------------------------
    def load_db(self):
        """Load and process the access database file (.accdb)."""
        try:
            accdb_file = get_accdb_file()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
            return

        try:
            dataframes = read_accdb_tables(accdb_file)
        except Exception as e:
            QMessageBox.critical(self, "Database Read Error", f"Failed to read database: {e}")
            return

        # Expect 'master_list' from read_accdb_tables
        if "master_list" not in dataframes:
            QMessageBox.critical(self, "Data Error", "master_list not created from database.")
            return

        self.AFFIF_DATA_labelEdit.setText(os.path.basename(str(accdb_file)))
        self.df_master_list = dataframes["master_list"]
        self.process_master_list()

        self.AFFIF_DATA_ICON_label.show()
        self.populate_selected_columns()

    def load_custom(self):
        """Load user-supplied CSV into df_master_list via file dialog (starting in CUSTOM_DIR)."""
        start_dir = str(CUSTOM_DIR) if CUSTOM_DIR.exists() else ""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV file", start_dir, "CSV Files (*.csv)")
        if not file_path:
            return
        try:
            CUSTOM = pd.read_csv(file_path)
        except Exception as e:
            QMessageBox.critical(self, "CSV Error", f"Failed to read CSV: {e}")
            return
        self.CUSTOM_DATA_labelEdit.setText(os.path.basename(file_path))
        self.df_master_list = CUSTOM
        self.process_master_list()
        self.CUSTOM_DATA_ICON_label.show()
        self.populate_selected_columns()

    def process_master_list(self):
        """Prepare master list with expected columns."""
        # Ensure df_master_list exists
        if not hasattr(self, "df_master_list") or self.df_master_list is None:
            self.df_master_list = pd.DataFrame()
            return

        # If expected columns for ICAO split exist, normalize
        # Safely replace empty strings with None for 'icao_rgn' and 'icao_code' if they exist
        for col in ("icao_rgn", "icao_code"):
            if col in self.df_master_list.columns:
                self.df_master_list[col] = self.df_master_list[col].replace(r"^\s*$", None, regex=True)

        # Create ICAO column
        self.create_icao_column()
        # Create runway id and distances
        self.create_runway_columns()

    def create_icao_column(self):
        """Create the ICAO column from icao_rgn and icao_code if possible."""
        if "icao_rgn" in self.df_master_list.columns and "icao_code" in self.df_master_list.columns:
            self.df_master_list["icao"] = self.df_master_list.apply(
                lambda row: f"{row['icao_rgn']}{row['icao_code']}" if row["icao_rgn"] and row["icao_code"] else "-",
                axis=1,
            )
        else:
            # If not present, ensure column exists (fill with '-' if missing)
            if "icao" not in self.df_master_list.columns:
                self.df_master_list["icao"] = "-"

    def create_runway_columns(self):
        """Create runway ID and compute runway distances (rw_dist)."""
        if "hi_ident" in self.df_master_list.columns and "lo_ident" in self.df_master_list.columns:
            self.df_master_list["rwy_id"] = self.df_master_list.apply(
                lambda row: f"RWY {row['hi_ident']}-{row['lo_ident']}" if row["hi_ident"] and row["lo_ident"] else "-",
                axis=1,
            )
        else:
            if "rwy_id" not in self.df_master_list.columns:
                self.df_master_list["rwy_id"] = "-"

        # Calculate runway distances safely
        self.calculate_runway_distances()

    def calculate_runway_distances(self):
        """Calculate distances between runway endpoints, result in feet (integer as string)."""
        def calc(row):
            try:
                if (
                    pd.notnull(row.get("hi_wgs_lat")) and pd.notnull(row.get("hi_wgs_long"))
                    and pd.notnull(row.get("lo_wgs_lat")) and pd.notnull(row.get("lo_wgs_long"))
                ):
                    meters = distance(
                        (row["hi_wgs_lat"], row["hi_wgs_long"]),
                        (row["lo_wgs_lat"], row["lo_wgs_long"]),
                        ellipsoid="WGS84",
                        method="great_circle",
                        back_az=False,
                    )[1]
                    return str(math.ceil(meters * 3.28084))
            except Exception:
                # If distance calculation fails for a row, return '-'
                return "-"
            return "-"

        # Apply only if df has been set
        if hasattr(self, "df_master_list") and not self.df_master_list.empty:
            self.df_master_list["rw_dist"] = self.df_master_list.apply(calc, axis=1)
            self.df_master_list["rw_dist"] = pd.to_numeric(self.df_master_list["rw_dist"], errors="coerce")
        else:
            # Ensure rw_dist exists as column
            if "rw_dist" not in self.df_master_list.columns:
                self.df_master_list["rw_dist"] = pd.Series(dtype="float64")

    # -------------------------
    # Table/search UI helpers
    # -------------------------

    def search_table(self, text=""):
        """
        Search the table based on the selected column and text.
        Shows/hides rows in the current QStandardItemModel.
        """
        model = self.DATABASE_AIRFIELDS_tableView.model()
        if model is None:
            return

        column_name = self.DATABASE_AIRFIELDS_comboBox.currentText()
        df_column = self.DISPLAY_COLUMN_MAPPING.get(column_name)
        if df_column is None:
            return

        # column_index in the view: headers include checkbox column at index 0
        # so find the header that matches the display label
        column_index = self.get_column_index_by_label(model, column_name)
        if column_index == -1:
            return

        self.update_row_visibility(model, column_index, text)

    def get_column_index_by_label(self, model, label):
        """Return the model column index for a given header label (exact match)."""
        for i in range(model.columnCount()):
            hd = model.headerData(i, Qt.Horizontal)
            if hd == label or str(hd).upper() == str(label).upper():
                return i
        # If not found by label, attempt reasonable fallback:
        # headers are [' ', 'WAC#','NAME','ICAO','RWY ID','RWY LEN(ft)'] in create_table_model
        header_map = {
            "WAC#": 1,
            "NAME": 2,
            "ICAO": 3,
            "RWY ID": 4,
            "RWY LEN(ft)": 5,
        }
        return header_map.get(label, -1)

    def update_row_visibility(self, model, column_index, text):
        """Hide rows that don't match the search text (case-insensitive)."""
        matched_index = None
        for row in range(model.rowCount()):
            index = model.index(row, column_index)
            item = model.data(index)
            match = False
            if item is not None:
                try:
                    match = text.lower() in str(item).lower() if text else True
                except Exception:
                    match = False
            self.DATABASE_AIRFIELDS_tableView.setRowHidden(row, not match)
            if match and matched_index is None:
                matched_index = model.index(row, column_index)
        if matched_index:
            self.DATABASE_AIRFIELDS_tableView.scrollTo(matched_index, QTableView.PositionAtCenter)

    def refilter_table(self):
        """Clear search input and repopulate based on filters."""
        try:
            self.DATABASE_AIRFIELDS_SEARCH_lineEdit.setText("")
        except Exception:
            pass
        if hasattr(self, "df_master_list"):
            self.populate_selected_columns()

    def eventFilter(self, obj, event):
        """Handle Enter key for distance input to reapply filters."""
        try:
            if (
                obj == self.AIRFIELD_OPERAND__DISTANCE_lineEdit
                and event.type() == event.KeyPress
                and event.key() in [Qt.Key_Return, Qt.Key_Enter]
            ):
                self.refilter_table()
                return True
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def apply_airfield_filters(self):
        """Apply distance and ICAO filters and store in self.filtered_df."""
        df = self.df_master_list.copy() if hasattr(self, "df_master_list") else pd.DataFrame()
        df = self.apply_distance_filter(df)
        df = self.apply_icao_filter(df)
        self.filtered_df = df

    def apply_distance_filter(self, df):
        """Apply numeric distance filter based on operand and value."""
        try:
            distance_val = int(self.AIRFIELD_OPERAND__DISTANCE_lineEdit.text())
            operand = self.AIRFIELD_OPERAND_comboBox.currentText()
            # Ensure rw_dist numeric
            if "rw_dist" in df.columns:
                df["rw_dist"] = pd.to_numeric(df["rw_dist"], errors="coerce")
                if operand == "<":
                    return df[df["rw_dist"] < distance_val]
                elif operand == ">":
                    return df[df["rw_dist"] > distance_val]
        except Exception:
            # If parse fails, return original df
            return df
        return df

    def apply_icao_filter(self, df):
        """Filter by ICAO search text (case-insensitive contains)."""
        try:
            icao_filter = self.DATABASE_AIRFIELDS_SEARCH_lineEdit.text().strip().upper()
        except Exception:
            icao_filter = ""
        if icao_filter and "icao" in df.columns:
            try:
                return df[df["icao"].str.upper().str.contains(icao_filter, na=False)]
            except Exception:
                return df
        return df

    def populate_selected_columns(self):
        """Apply filters and update table view model."""
        self.apply_airfield_filters()
        df = getattr(self, "filtered_df", pd.DataFrame())

        # Update row count label
        self.update_row_count_label(df)

        # Create model and configure view
        model = self.create_table_model(df)
        self.setup_table_view(model)

    def update_row_count_label(self, df):
        """Show count of filtered vs total runways if master exists."""
        total = len(self.df_master_list) if hasattr(self, "df_master_list") else 0
        filtered = len(df)
        try:
            label_text = f"{filtered:,}/{total:,} runways loaded" if filtered != total else f"{total:,} runways loaded"
            self.DATABASE_AIRFIELDS_LOADED_label.setText(label_text)
        except Exception:
            pass

    def create_table_model(self, df):
        """Create QStandardItemModel from dataframe safely (handles missing columns)."""
        # Keep display columns consistent with mapping
        display_columns = ["wac_innr", "arpt_name", "icao", "rwy_id", "rw_dist"]
        # Reindex to ensure columns exist; missing filled with '-'
        selected_cols = df.reindex(columns=display_columns, fill_value="-")

        model = QStandardItemModel()
        headers = [" "] + ["WAC#", "NAME", "ICAO", "RWY ID", "RWY LEN(ft)"]
        model.setHorizontalHeaderLabels(headers)

        for idx, (_, row) in enumerate(selected_cols.iterrows()):
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setEditable(False)
            # Store the original dataframe index (if any) in UserRole for retrieval
            df_index = row.name
            checkbox_item.setData(df_index, Qt.UserRole)

            text_items = []
            for col_name in display_columns:
                cell = row[col_name]
                item = QStandardItem(str(cell))
                if col_name == "rw_dist":
                    try:
                        # store numeric for sorting/display role
                        val = float(cell) if cell not in ("-", None, "") else None
                        if val is not None:
                            item.setData(val, Qt.DisplayRole)
                    except Exception:
                        pass
                item.setEditable(False)
                text_items.append(item)

            model.appendRow([checkbox_item] + text_items)

        return model

    def handle_redux_change(self, item):
        """Style REDUX cell when changed. Do not mutate master df here—update on CONTINUE."""
        try:
            col = item.column()
            # In the customTable the redux columns were set to col indices 1 and 3
            if col in (1, 3):
                try:
                    value = int(item.text())
                except Exception:
                    value = None
                font = QFont()
                if value is not None and value != 0:
                    font.setBold(True)
                    item.setFont(font)
                    item.setForeground(QBrush(QColor("#00FF00")))
                else:
                    font.setBold(False)
                    item.setFont(font)
                    item.setForeground(QBrush(QColor("white")))
        except Exception:
            pass

    def setup_table_view(self, model):
        """Attach model to table view and apply UI sizing/formatting."""
        table = self.DATABASE_AIRFIELDS_tableView
        table.setModel(model)

        # Apply the search filter (keeps hidden rows hidden)
        try:
            self.search_table(self.DATABASE_AIRFIELDS_SEARCH_lineEdit.text())
        except Exception:
            pass

        # Hide vertical header
        try:
            table.verticalHeader().setVisible(False)
        except Exception:
            pass

        # Resize and set sensible widths (guarded)
        try:
            table.resizeColumnsToContents()
            header = table.horizontalHeader()
            # Basic widths; if model has fewer columns, guard against IndexError
            table.setColumnWidth(0, 30)  # checkbox
            if model.columnCount() >= 6:
                table.setColumnWidth(1, 120)  # WAC#
                table.setColumnWidth(2, 200)  # NAME (stretch)
                table.setColumnWidth(3, 80)  # ICAO
                table.setColumnWidth(4, 140)  # RWY ID
                table.setColumnWidth(5, 100)  # RWY LEN(ft)
                header.setSectionResizeMode(2, header.Stretch)
        except Exception:
            pass

        # Reset horizontal scroll to start
        try:
            table.horizontalScrollBar().setValue(table.horizontalScrollBar().minimum())
        except Exception:
            pass

    # -------------------------
    # Selection & processing entry points
    # -------------------------
    def select_all_rows(self):
        """Toggle selection (checkbox) for all visible rows."""
        model = self.DATABASE_AIRFIELDS_tableView.model()
        if model is None:
            return

        visible_rows = [r for r in range(model.rowCount()) if not self.DATABASE_AIRFIELDS_tableView.isRowHidden(r)]
        all_checked = True
        for row in visible_rows:
            item = model.item(row, 0)
            if item is None or item.checkState() != Qt.Checked:
                all_checked = False
                break

        new_state = Qt.Unchecked if all_checked else Qt.Checked
        for row in visible_rows:
            item = model.item(row, 0)
            if item:
                item.setCheckState(new_state)

        try:
            self.selectAllpushButton.setText("Deselect All" if new_state == Qt.Checked else "Select All")
        except Exception:
            pass

    def get_checked_visible_indices(self, model):
        """Get indices of checked and visible rows (safe & verbose)."""
        df_indices = []
        # Defensive: ensure model exists
        if model is None:
            print("DEBUG: get_checked_visible_indices - model is None")
            return df_indices
    
        for row in range(model.rowCount()):
            # Skip hidden rows
            try:
                if self.DATABASE_AIRFIELDS_tableView.isRowHidden(row):
                    continue
            except Exception:
                # If isRowHidden fails, don't skip
                pass
    
            checkbox_item = model.item(row, 0)
            if not checkbox_item:
                # No checkbox at this row
                continue
    
            try:
                checked = checkbox_item.checkState() == Qt.Checked
            except Exception:
                checked = False
    
            if checked:
                # The code stores the original dataframe index in Qt.UserRole
                df_index = checkbox_item.data(Qt.UserRole)
                # If we stored None earlier, fall back to using the model row number mapping.
                if df_index is None:
                    # If model rows map to filtered_df sequentially, map by visible row:
                    # Try to map using a visible-row -> filtered_df index mapping
                    try:
                        # model's row order corresponds to filtered_df.reset_index(drop=False).index ordering,
                        # but simpler approach: if there's a 'icao' column cell in column 3, try to find the df row by matching values.
                        cell_index = model.index(row, 1)  # column 1 is WAC# (or adjust if needed)
                        cell_val = model.data(cell_index)
                        # Attempt best-effort lookup in filtered_df
                        if hasattr(self, "filtered_df") and not self.filtered_df.empty:
                            possible = self.filtered_df.index[self.filtered_df["wac_innr"].astype(str) == str(cell_val)]
                            if len(possible) > 0:
                                df_index = int(possible[0])
                    except Exception:
                        df_index = None
                if df_index is not None:
                    df_indices.append(df_index)
        print(f"DEBUG: get_checked_visible_indices -> found {len(df_indices)} indices: {df_indices}")
        return df_indices
    
    
    def collect_checked_rows(self):
        """Process the checked rows and show rwyModWidget (or ICAO prompt) as appropriate."""
        model = self.DATABASE_AIRFIELDS_tableView.model()
        if model is None:
            print("DEBUG: collect_checked_rows - no model attached to table view")
            QMessageBox.information(self, "No data", "No table data is loaded. Load AFFIF or CUSTOM first.")
            return
    
        df_indices = self.get_checked_visible_indices(model)

        if not df_indices:
            # No rows selected
            print("DEBUG: collect_checked_rows - no checked rows found")
            QMessageBox.information(self, "No selection", "No rows are selected for processing.")
            self.df2proc = pd.DataFrame()
            return
    
        # Try to build df2proc using .loc if filtered_df uses original indices,
        # otherwise try iloc for positional mapping.
        try:
            # If filtered_df uses original index labels, use .loc
            self.df2proc = self.filtered_df.loc[df_indices].reset_index(drop=True)
        except Exception as e_loc:
            print(f"DEBUG: collect_checked_rows - .loc failed ({e_loc}), trying .iloc with positions")
            try:
                # If df_indices are positions, use .iloc
                self.df2proc = self.filtered_df.iloc[df_indices].reset_index(drop=True)
            except Exception as e_iloc:
                print(f"DEBUG: collect_checked_rows - .iloc failed ({e_iloc})")
                QMessageBox.critical(self, "Selection Error", "Failed to collect selected rows.")
                self.df2proc = pd.DataFrame()
                return
    
        print(f"DEBUG: collect_checked_rows - {len(self.df2proc)} runways selected for processing")
        # Determine ICAO (safe)
        self.icao = "-"
        if "icao" in self.df2proc.columns and len(self.df2proc) > 0:
            try:
                self.icao = str(self.df2proc.icao.iloc[0]).strip()
            except Exception:
                self.icao = "-"
    
        # If ICAO is missing or '-', prompt user to enter one
        if not is_valid_icao(self.icao):
            print(f"DEBUG: collect_checked_rows - invalid ICAO ('{self.icao}'), prompting user")
            # visually indicate the Add_ICAO_lineEdit and show the Add_ICAO prompt widget
            try:
                self.Add_ICAO_lineEdit.setStyleSheet(
                    """
                    QLineEdit {
                        background-color: #2b2b2b;
                        border: 1px solid #FF0000;
                        color: #FF0000;
                        border-radius: 4px;
                        padding: 4px;
                    }
                    """
                )
                # optional: pre-fill with empty or '-' to indicate missing
                self.Add_ICAO_lineEdit.setText("")
                self.Add_ICAO_QWidget.show()
            except Exception:
                # fallback: message box
                QMessageBox.warning(self, "Missing ICAO", "Selected runways lack a valid ICAO. Please enter one.")
            return
    
        # Show runway modification widget (safe-show)
        try:
            print("DEBUG: collect_checked_rows - showing rwyModWidget")
            self.show_rwyModWidget()
        except Exception as e:
            print(f"DEBUG: collect_checked_rows - failed to show rwyModWidget: {e}")
            # fallback: proceed without mod dialog
            self.df2proc["hi_redux"] = 0
            self.df2proc["lo_redux"] = 0
            self.save_output_files()

    def process_selected_rows(self, df_indices):
        """Alternate entrypoint: process rows given explicit df indices (used by other features)."""
        if not hasattr(self, "filtered_df"):
            QMessageBox.warning(self, "Processing Error", "No filtered data available to process.")
            return
        try:
            self.df2proc = self.filtered_df.loc[df_indices].reset_index(drop=True)
        except Exception:
            self.df2proc = pd.DataFrame()
        if self.df2proc.empty:
            QMessageBox.warning(self, "Processing Error", "No rows selected for processing.")
            return
        print(f"{len(self.df2proc)} Runways selected for processing.")
        self.icao = str(self.df2proc.icao.iloc[0]) if "icao" in self.df2proc.columns else "-"
        self.save_output_files()
        
    def show_rwyModWidget(self):
        """
        Ensure rwyModWidget appears in front and is focused.
        Replaces simple self.show_rwyModWidget() calls.
        """
        try:
            if not hasattr(self, "rwyModWidget") or self.rwyModWidget is None:
                print("DEBUG: show_rwyModWidget - rwyModWidget attribute missing")
                return
    
            w = self.rwyModWidget
    
            # Diagnostic output (useful when debugging)
            try:
                print(
                    "DEBUG: rwyModWidget state before show:",
                    f"isVisible={w.isVisible()}",
                    f"isEnabled={w.isEnabled()}",
                    f"parent={type(w.parent()).__name__ if w.parent() else None}",
                    f"flags={int(w.windowFlags())}",
                    f"geometry={w.geometry()}",
                )
            except Exception:
                pass
    
            # Make it a top-level window so show() brings it forward. This is safe:
            # if it's already top-level this just preserves the flag.
            w.setWindowFlags(w.windowFlags() | Qt.Window)
    
            # Optional: set application modal so it grabs focus (uncomment if desired)
            # w.setWindowModality(Qt.ApplicationModal)
    
            # Show, raise and activate to bring to front
            w.show()
            w.raise_()
            w.activateWindow()
    
            # Post-show diagnostic
            try:
                print("DEBUG: show_rwyModWidget - now visible:", w.isVisible())
            except Exception:
                pass
    
        except Exception as e:
            print("DEBUG: show_rwyModWidget exception:", e)
            # Fallback: try making it visible in-place
            try:
                if hasattr(self, "rwyModWidget") and self.rwyModWidget:
                    self.rwyModWidget.setVisible(True)
            except Exception:
                pass
    
    
    
    # -------------------------
    # Runway modification UI handlers
    # -------------------------
    def handle_rwyMod_yes(self):
        """User wants to edit REDUX values in a custom table before saving."""
        self.rwyModWidget.hide()
        # Ensure df2proc has the redux columns
        self.df2proc["hi_redux"] = 0
        self.df2proc["lo_redux"] = 0

        table = self.customTable
        model = QStandardItemModel()
        table.setModel(model)

        headers = ["RWY", "REDUX", "RWY", "REDUX"]
        model.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)

        # Column sizing
        try:
            table.setColumnWidth(0, 80)
            table.setColumnWidth(1, 50)
            table.setColumnWidth(2, 80)
            table.setColumnWidth(3, 50)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        except Exception:
            pass

        # Fill hi_ident and hi_redux
        for i, ident in enumerate(self.df2proc.get("hi_ident", [])):
            model.setItem(i, 0, QStandardItem(str("RWY " + str(ident))))
            item = QStandardItem(str(self.df2proc.get("hi_redux", [0] * len(self.df2proc))[i]))
            item.setEditable(True)
            model.setItem(i, 1, item)

        # Fill lo_ident and lo_redux (assume same row counts or fill missing)
        for j, ident in enumerate(self.df2proc.get("lo_ident", [])):
            model.setItem(j, 2, QStandardItem(str("RWY " + str(ident))))
            item = QStandardItem(str(self.df2proc.get("lo_redux", [0] * len(self.df2proc))[j]))
            item.setEditable(True)
            model.setItem(j, 3, item)

        model.itemChanged.connect(self.handle_redux_change)
        self.rwymodtable.show()

    def handle_rwyMod_no(self):
        """User doesn't want to edit redux values."""
        try:
            self.rwyModWidget.hide()
        except Exception:
            pass
        self.df2proc["hi_redux"] = 0
        self.df2proc["lo_redux"] = 0
        self.save_output_files()

    def handle_rwymodtable(self):
        """Extract redux values from the customTable model and write back to df2proc."""
        model = self.customTable.model()
        if model is None:
            QMessageBox.warning(self, "RWY Edit", "No runway modification table available.")
            return

        hi_count = len(self.df2proc.get("hi_ident", []))
        lo_count = len(self.df2proc.get("lo_ident", []))

        updated_hi_redux = []
        for i in range(hi_count):
            item = model.item(i, 1)
            updated_hi_redux.append(item.text() if item else "0")

        updated_lo_redux = []
        for j in range(lo_count):
            item = model.item(j, 3)
            updated_lo_redux.append(item.text() if item else "0")

        # Assign back to df2proc (lengths should match or will broadcast/truncate)
        try:
            self.df2proc["hi_redux"] = updated_hi_redux
            self.df2proc["lo_redux"] = updated_lo_redux
        except Exception:
            # Last resort: add columns length-matched
            self.df2proc = self.df2proc.copy()
            self.df2proc["hi_redux"] = pd.Series(updated_hi_redux)
            self.df2proc["lo_redux"] = pd.Series(updated_lo_redux)

        print("Updated REDUX values saved to df2proc.")
        try:
            self.rwymodtable.hide()
        except Exception:
            pass
        self.save_output_files()

    def set_icao_from_input(self):
        """Set ICAO entered by the user in the Add_ICAO widget."""
        try:
            typed_value = self.Add_ICAO_lineEdit.text().strip().upper()
        except Exception:
            typed_value = ""
        if len(typed_value) <= 4 and is_valid_icao(typed_value):
            self.icao = typed_value
            try:
                self.Add_ICAO_QWidget.hide()
            except Exception:
                pass
        else:
            # Truncate or refuse invalid ICAO
            self.icao = typed_value[:4] if typed_value else "-"
            if not is_valid_icao(self.icao):
                QMessageBox.warning(self, "ICAO", "Entered ICAO appears invalid.")

    def on_icao_text_changed(self, text):
        """Visual feedback while typing ICAO."""
        try:
            if len(text) == 4:
                self.Add_ICAO_lineEdit.setStyleSheet(
                    """
                    QLineEdit {
                        background-color: #2b2b2b;
                        border: 1px solid #00FF00;
                        color: #00FF00;
                        border-radius: 4px;
                        padding: 4px;
                    }
                    """
                )
                self.Add_ICAO_button1.show()
            else:
                self.Add_ICAO_lineEdit.setStyleSheet(
                    """
                    QLineEdit {
                        background-color: #2b2b2b;
                        border: 1px solid #FF0000;
                        color: #FF0000;
                        border-radius: 4px;
                        padding: 4px;
                    }
                    """
                )
        except Exception:
            pass

    # -------------------------
    # Saving and output generation
    # -------------------------
    def save_output_files(self):
        """Save processed dataframe to CSV and generate KML/XML outputs."""
        if not hasattr(self, "df2proc") or self.df2proc is None or self.df2proc.empty:
            QMessageBox.warning(self, "No Data", "No processed data to save.")
            return

        if not hasattr(self, "icao") or not is_valid_icao(self.icao):
            QMessageBox.warning(self, "ICAO", "Invalid ICAO; cannot save outputs.")
            return

        try:
            icao_path = make_returns_path(self.icao)
        except Exception as e:
            QMessageBox.critical(self, "Path Error", f"Failed to create output directory: {e}")
            return

        csv_path = icao_path / f"{self.icao}_CHECKED_RWYS.csv"
        try:
            self.df2proc.to_csv(str(csv_path), index=False)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save CSV: {e}")
            return

        # Mirror runways (both_runways) - robust to empty and mismatched columns
        def both_runways(df2proc: pd.DataFrame) -> pd.DataFrame:
            hi_cols = [col for col in df2proc.columns if col.startswith("hi_")]
            lo_cols = [col for col in df2proc.columns if col.startswith("lo_")]

            swap_pairs = []
            for hi in hi_cols:
                suffix = hi[3:]
                lo = f"lo_{suffix}"
                if lo in lo_cols:
                    swap_pairs.append((hi, lo))

            new_rows = []
            for _, row in df2proc.iterrows():
                rwy = row.copy()
                inv_rwy = row.copy()
                for col1, col2 in swap_pairs:
                    try:
                        inv_rwy[col1], inv_rwy[col2] = row[col2], row[col1]
                    except Exception:
                        # if swapping fails for a particular pair, skip it
                        continue
                new_rows.extend([rwy, inv_rwy])

            if not new_rows:
                # Return empty DataFrame with same columns
                return pd.DataFrame(columns=df2proc.columns)
            try:
                return pd.DataFrame(new_rows, columns=df2proc.columns)
            except Exception:
                # Fallback: build from list of dicts
                return pd.DataFrame([r.to_dict() for r in new_rows])

        try:
            self.df2proc = both_runways(self.df2proc)
        except Exception:
            # Leave df2proc as-is if mirroring fails
            pass

        # Call external generation functions (wrapped)
        try:
            makerunway_kml(
                self.df2proc,
                self.icao,
                self.TD_Dist_lineEdit.text(),
                self.STP_Dist_lineEdit.text(),
                self.G_Slope_lineEdit.text(),
                self.TP_Alt_lineEdit.text(),
                self.RWY_W_Value_label.text(),
                self.GA_Spd_lineEdit.text(),
                self.Dep_pt_lineEdit.text(),
            )
            makerunway_xml(
                self.df2proc,
                self.icao,
                self.TD_Dist_lineEdit.text(),
                self.STP_Dist_lineEdit.text(),
                self.G_Slope_lineEdit.text(),
                self.TP_Alt_lineEdit.text(),
                self.RWY_W_Value_label.text(),
                self.GA_Spd_lineEdit.text(),
                self.Dep_pt_lineEdit.text(),
            )
        except Exception as e:
            QMessageBox.critical(self, "Generation Error", f"Failed to create runway files: {e}")
            return

        print("Complete")

    def closeEvent(self, event):
        """Handle window close event - restore original streams."""
        if self.console:
            self.console.restore()
        super().closeEvent(event)

    # -------------------------
    # Dialog launching methods using DialogFactory
    # -------------------------
    def open_dialog(self, key, params=None):
        """
        Open a dialog using the DialogFactory.
        
        Args:
            key: Registry key for the dialog.
            params: Optional parameters for the dialog.
            
        Returns:
            Dialog result or None if canceled.
        """
        try:
            dialog = self.factory.create_dialog(key, parent=self, params=params)
            result = dialog()
            if result and hasattr(self, "CMDwindow"):
                self.CMDwindow.appendPlainText(str(result))
            return result
        except KeyError as e:
            print(f"Dialog '{key}' not found: {e}")
            return None
        except Exception as e:
            print(f"Error opening dialog: {e}")
            return None


# -------------------------
# Application entrypoint
# -------------------------
def main():
    """Main entry point for the ATOL application."""
    # Validate license at startup
    if not validate_license():
        print("License validation failed. Continuing in demo mode.")
    
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()