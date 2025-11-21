""" 
ATOL v3 Main Application
Created on Thu Jul 24 12:28:17 2025
@author: dukes 

This application handles airfield database management and runway processing.
It provides filtering, searching, and processing capabilities for airfield data.
"""

import sys 
import os 
import pandas as pd 
import math
from pathlib import Path
from PyQt5.uic import loadUi 
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableView, QHeaderView, QFileDialog) 
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QFont
from PyQt5.QtCore import Qt
import io

# Local imports
from accdb_reader import read_accdb_tables 
from simple_distance import distance 
from runwaykml import makerunway_kml
from runwayxml import makerunway_xml

class EmittingSream(io.StringIO):
    def __init__ (self, text_edit):
        super().__init__()
        self.text_edit = text_edit
    
    def write(self, text):
        self.text_edit.moveCursor(self.text_edit.textCursor().End)
        self.text_edit.insertPlainText(text)
        QApplication.processEvents()

class MainWindow(QMainWindow):
    """
    Main application window for the ATOL v3 interface.
    Handles database loading, filtering, and runway .kml and .xml processing.
    """
    
    def __init__(self):
        super().__init__()
        self.initialize_ui()
        self.setup_initial_values()
        self.connect_signals()

    def initialize_ui(self):
        """Initialize the user interface from the UI file"""
        ui_path = os.path.join(os.path.dirname(__file__), 'GUI', 'MAIN.ui')
        loadUi(ui_path, self)
        
        
        sys.stdout = EmittingSream(self.CMDwindow)
        
        # Hide and clear initial elements
        self.AFFIF_DATA_ICON_label.hide()
        self.AFFIF_DATA_labelEdit.setText('') #FSDFSDFSDF
        
        #Widget Hides
        self.rwyModWidget.hide()
        self.rwymodtable.hide()
        self.Add_ICAO_QWidget.hide()
        self.Add_ICAO_button1.hide()
        
        self.CUSTOM_DATA_ICON_label.hide()
        self.CUSTOM_DATA_labelEdit.setText('')
        
        # Initialize combo boxes
        self.setup_combo_boxes()
        
    def setup_combo_boxes(self):
        """Setup combo boxes with initial values"""
        # Airfield operator combo setup
        self.AIRFIELD_OPERAND_comboBox.clear()
        self.AIRFIELD_OPERAND_comboBox.addItems(['>', '<'])
        
        # Database fields combo setup
        self.DATABASE_AIRFIELDS_comboBox.clear()
        self.DATABASE_AIRFIELDS_comboBox.addItems(['ICAO', 'WAC#', 'NAME'])
        
        # Set default distance
        self.AIRFIELD_OPERAND__DISTANCE_lineEdit.setText("7999")
        

    def setup_initial_values(self):
        """Initialize class variables from UI elements"""
        # Store initial values from line edits
        self.TD_Dist = self.TD_Dist_lineEdit.text()
        self.STP_Dist = self.STP_Dist_lineEdit.text()
        self.G_Slope = self.G_Slope_lineEdit.text()
        self.TP_alt = self.TP_Alt_lineEdit.text()  # In feet
        self.GA_spd = self.GA_Spd_lineEdit.text()
        
    def connect_signals(self):
        """Connect all UI signals to their respective slots"""
        # Button connections
        self.AFFIF_DATA_pushButton.clicked.connect(self.load_db)
        self.CUSTOM_DATA_pushButton.clicked.connect(self.load_custom)
        self.selectAllpushButton.clicked.connect(self.select_all_rows)
        self.PROCESS_SELECTED_pushButton.clicked.connect(self.collect_checked_rows)
        self.Add_ICAO_button1.clicked.connect(self.set_icao_from_input)
        self.Add_ICAO_lineEdit.textChanged.connect(self.on_icao_text_changed)
        self.Add_ICAO_button1.clicked.connect(self.rwyModWidget.show)
        
        # Search and filter connections
        self.DATABASE_AIRFIELDS_SEARCH_lineEdit.textChanged.connect(self.search_table)
        self.DATABASE_AIRFIELDS_comboBox.currentTextChanged.connect(
            lambda: self.search_table(self.DATABASE_AIRFIELDS_SEARCH_lineEdit.text())
        )
        
        # Distance filter connections
        self.AIRFIELD_OPERAND_comboBox.currentTextChanged.connect(self.refilter_table)
        self.AIRFIELD_OPERAND__DISTANCE_lineEdit.installEventFilter(self)
        
        # Setup additional connections
        self.setup_connections()

    def setup_connections(self):
        """Setup additional connections for filtering and updates"""
        self.AIRFIELD_OPERAND_comboBox.currentIndexChanged.connect(self.populate_selected_columns)
        self.AIRFIELD_OPERAND__DISTANCE_lineEdit.returnPressed.connect(self.populate_selected_columns)
        self.AIRFIELD_OPERAND__DISTANCE_lineEdit.editingFinished.connect(self.populate_selected_columns)
        self.rwyModWidget_YES.clicked.connect(self.handle_rwyMod_yes)
        self.rwyModWidget_NO.clicked.connect(self.handle_rwyMod_no)
        self.rwymodtable_CONTINUE.clicked.connect(self.handle_rwymodtable)

    def load_db(self):
        """Load and process the access database file"""
        # Load the first .accdb file found in the AFFIF directory
        accdb_file = list(Path('../../AFFIF').glob('*.accdb'))[0]
        dataframes = read_accdb_tables(accdb_file)
        self.AFFIF_DATA_labelEdit.setText(os.path.basename(accdb_file))
        
        # Store the master list and process it
        self.df_master_list = dataframes['master_list']
        self.process_master_list()
        
        # Show the data is loaded and populate the table
        self.AFFIF_DATA_ICON_label.show()
        self.populate_selected_columns()
        
    def load_custom(self):
        """Load and process the CUSTOM file"""
        # Load the first .accdb file found in the AFFIF directory
        # accdb_file = list(Path('../../AFFIF').glob('*.accdb'))[0]
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV file", "", "CSV Files (*.csv)")
        if file_path:
            self.df = pd.read_csv(file_path)
            print(f"{os.path.basename(file_path)} loaded")

        # file_path = r'C:\Users\dukes\Sync\AriesCI\ATOLv4_2025\FINAL\CUSTOM_ICAO\KXXX_RWYS.csv'
            # print(f"Loaded {len(self.df)} rows from {file_path}")
            CUSTOM = pd.read_csv(file_path)
            # dataframes = CUSTOM
            self.CUSTOM_DATA_labelEdit.setText(os.path.basename(file_path))
            
            # Store the master list and process it
            self.df_master_list = CUSTOM
            self.process_master_list()
            
            # Show the data is loaded and populate the table
            self.CUSTOM_DATA_ICON_label.show()
            self.populate_selected_columns()   
        
        

    def process_master_list(self):
        """Process the master list dataframe to create required columns"""
        # Clean up ICAO data
        self.df_master_list[['icao_rgn', 'icao_code']] = self.df_master_list[['icao_rgn', 'icao_code']].replace(
            r'^\s*$', None, regex=True
        )
        
        # Create ICAO and runway ID columns
        self.create_icao_column()
        self.create_runway_columns()

    def create_icao_column(self):
        """Create the ICAO column from region and code"""
        self.df_master_list['icao'] = self.df_master_list.apply(
            lambda row: f"{row['icao_rgn']}{row['icao_code']}" 
            if row['icao_rgn'] and row['icao_code'] else "-",
            axis=1
        )

    def create_runway_columns(self):
        """Create runway ID and distance columns"""
        # Create runway ID
        self.df_master_list['rwy_id'] = self.df_master_list.apply(
            lambda row: f"RWY {row['hi_ident']}-{row['lo_ident']}" 
            if row['hi_ident'] and row['lo_ident'] else "-",
            axis=1
        )
        
        # Calculate runway distance
        self.calculate_runway_distances()

    def calculate_runway_distances(self):
        """Calculate distances between runway endpoints"""
        self.df_master_list['rw_dist'] = self.df_master_list.apply(
            self.calculate_single_runway_distance,
            axis=1
        )
        self.df_master_list['rw_dist'] = pd.to_numeric(self.df_master_list['rw_dist'], errors='coerce')

    def calculate_single_runway_distance(self, row):
        """Calculate distance for a single runway"""
        if (pd.notnull(row['hi_wgs_lat']) and pd.notnull(row['hi_wgs_long']) 
            and pd.notnull(row['lo_wgs_lat']) and pd.notnull(row['lo_wgs_long'])):
            return str(math.ceil(distance(
                (row['hi_wgs_lat'], row['hi_wgs_long']),
                (row['lo_wgs_lat'], row['lo_wgs_long']),
                ellipsoid='WGS84',
                method='great_circle',
                back_az=False)[1] * 3.28084))
        return "-"

    def search_table(self, text=""):
        """
        Search the table based on the selected column and text
        Only shows rows that match the search criteria
        """
        model = self.DATABASE_AIRFIELDS_tableView.model()
        if not model:
            return
        
        # Get the selected column to search
        column_name = self.DATABASE_AIRFIELDS_comboBox.currentText()
        column_index = self.get_column_index(model, column_name)
        if column_index == -1:
            return
            
        # Search and update visibility
        self.update_row_visibility(model, column_index, text)

    def get_column_index(self, model, column_name):
        """Get the index of a column by its header name"""
        for i in range(model.columnCount()):
            if model.headerData(i, Qt.Horizontal) == column_name:
                return i
        return -1

    def update_row_visibility(self, model, column_index, text):
        """Update the visibility of rows based on search text"""
        matched_index = None
        
        for row in range(model.rowCount()):
            index = model.index(row, column_index)
            item = model.data(index)
            match = text.lower() in str(item).lower() if item else False
            
            self.DATABASE_AIRFIELDS_tableView.setRowHidden(row, not match)
            
            if match and matched_index is None:
                matched_index = index
                
        if matched_index:
            self.DATABASE_AIRFIELDS_tableView.scrollTo(matched_index, QTableView.PositionAtCenter)

    def refilter_table(self):
        """Clear search and reapply filters"""
        self.DATABASE_AIRFIELDS_SEARCH_lineEdit.setText("")
        if hasattr(self, "df_master_list"):
            self.populate_selected_columns()

    def eventFilter(self, obj, event):
        """Handle key press events for the distance line edit"""
        if (obj == self.AIRFIELD_OPERAND__DISTANCE_lineEdit 
            and event.type() == event.KeyPress
            and event.key() in [Qt.Key_Return, Qt.Key_Enter]):
            self.refilter_table()
            return True
        return super().eventFilter(obj, event)

    def apply_airfield_filters(self):
        """Apply distance and ICAO filters to the master list"""
        df = self.df_master_list.copy()
        
        # Apply distance filter
        df = self.apply_distance_filter(df)
        
        # Apply ICAO text filter
        df = self.apply_icao_filter(df)
        
        self.filtered_df = df

    def apply_distance_filter(self, df):
        """Apply the distance filter based on operator and value"""
        try:
            distance_val = int(self.AIRFIELD_OPERAND__DISTANCE_lineEdit.text())
            operand = self.AIRFIELD_OPERAND_comboBox.currentText()
            
            if operand == '<':
                return df[df['rw_dist'] < distance_val]
            elif operand == '>':
                return df[df['rw_dist'] > distance_val]
                
        except ValueError:
            pass
            
        return df

    def apply_icao_filter(self, df):
        """Apply the ICAO text filter"""
        icao_filter = self.DATABASE_AIRFIELDS_SEARCH_lineEdit.text().strip().upper()
        if icao_filter:
            return df[df['icao'].str.upper().str.contains(icao_filter)]
        return df

    def populate_selected_columns(self):
        """Populate the table view with filtered data"""
        self.apply_airfield_filters()
        df = self.filtered_df
        
        # Update the row count label
        self.update_row_count_label(df)
        
        # Create and populate the table model
        model = self.create_table_model(df)
        
        # Setup the table view
        self.setup_table_view(model)

    def update_row_count_label(self, df):
        """Update the label showing number of loaded runways"""
        total = len(self.df_master_list)
        filtered = len(df)
        label_text = (f"{filtered:,}/{total:,} runways loaded" 
                     if filtered != total else f"{total:,} runways loaded")
        self.DATABASE_AIRFIELDS_LOADED_label.setText(label_text)

    def create_table_model(self, df):
        """Create and populate the table model with data"""
        # Only select the columns we want to display
        display_columns = ['wac_innr', 'arpt_name', 'icao', 'rwy_id', 'rw_dist']
        selected_cols = df[display_columns]
    
        model = QStandardItemModel()
        headers = [' '] + ['WAC#', 'NAME', 'ICAO', 'RWY ID', 'RWY LEN(ft)']
        model.setHorizontalHeaderLabels(headers)
    
        # Add rows to the model
        for _, row in selected_cols.iterrows():
            # Create checkbox item
            checkbox_item = QStandardItem()
            checkbox_item.setCheckable(True)
            checkbox_item.setEditable(False)
            checkbox_item.setData(row.name, Qt.UserRole)
    
            # Create text items for visible columns
            text_items = []
            for col_name, cell in zip(display_columns, row):
                item = QStandardItem(str(cell))
                if col_name == 'rw_dist' and pd.notnull(cell):
                    item.setData(float(cell), Qt.DisplayRole)
                text_items.append(item)
    
        #     # Add editable REDUX column with default value 0
        #     redux_item = QStandardItem("0")
        #     redux_item.setEditable(True)
        #     redux_item.setData(0, Qt.DisplayRole)  # Ensures it's treated as an int
    
            # model.appendRow([checkbox_item] + text_items + [redux_item])
            model.appendRow([checkbox_item] + text_items)
        # model.itemChanged.connect(self.handle_redux_change)
        
        return model
    
    def handle_redux_change(self, item):
        """Style REDUX cell if value is changed from 0"""
        if item.column() == 1 or item.column() == 3:  # REDUX column index
            try:
                value = int(item.text())
            except ValueError:
                value = None
    
            font = QFont()
            if value != 0:
                font.setBold(True)
                item.setFont(font)
                item.setForeground(QBrush(QColor("#00FF00")))
                self.customTable.clearSelection()
                #Here is where we will update the value in 
                self.df_master_list['redux'] = self.df_master_list.apply(item)
                self.df_master_list['redux'] = pd.to_numeric(self.df_master_list['redux'], errors='coerce')

            else:
                font.setBold(False)
                item.setFont(font)
                item.setForeground(QBrush(QColor("white")))


    def setup_table_view(self, model):
        """Setup the table view with the model and formatting"""
        table = self.DATABASE_AIRFIELDS_tableView
        table.setModel(model)
        
        # Apply the search filter
        self.search_table()
        
        # Hide vertical header (row numbers)
        table.verticalHeader().setVisible(False)
        
        # Set column widths
        table.resizeColumnsToContents()  # First, size to content
        
        # Get the header
        header = table.horizontalHeader()
        
        # Set minimum width for checkbox column
        table.setColumnWidth(0, 30)  # Checkbox column
        
        # Set fixed widths for other columns except NAME and WAC#
        table.setColumnWidth(1, 120)  # ICAO
        table.setColumnWidth(3, 80)  # ICAO
        table.setColumnWidth(4, 140)  # RWY ID
        table.setColumnWidth(5, 100)  # RWY LEN(FT)
        
        # Make WAC# and NAME columns stretch
        # header.setSectionResizeMode(1, header.Stretch)  # WAC# column
        header.setSectionResizeMode(2, header.Stretch)  # NAME column
        
        # Reset horizontal scroll
        table.horizontalScrollBar().setValue(
            table.horizontalScrollBar().minimum()
        )

    def select_all_rows(self):
        """Select or deselect all visible rows in the table"""
        model = self.DATABASE_AIRFIELDS_tableView.model()
        if not model:
            return
        
        # Check if all visible rows are currently selected
        visible_rows = range(model.rowCount())
        all_checked = all(
            model.item(row, 0).checkState() == Qt.Checked 
            for row in visible_rows
        )
        
        # Toggle the check state
        new_state = Qt.Unchecked if all_checked else Qt.Checked
        for row in visible_rows:
            item = model.item(row, 0)
            if item:
                item.setCheckState(new_state)
        
        # Update button text
        self.selectAllpushButton.setText(
            "Deselect All" if new_state == Qt.Checked else "Select All"
        )


    def handle_rwyMod_yes(self):
        self.rwyModWidget.hide()
        
        #add redux columns
        self.df2proc['hi_redux'] = 0
        self.df2proc['lo_redux'] = 0
        
        table = self.customTable
        model = QStandardItemModel()
        table.setModel(model)      

        
        headers = ['RWY', 'REDUX', 'RWY', 'REDUX']
        model.setHorizontalHeaderLabels(headers)

        table.verticalHeader().setVisible(False)
    
        # Fix first column width and stretch second column
        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 50)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

    
        # Fill hi_ident and hi_redux
        for i, (ident, redux) in enumerate(zip(self.df2proc['hi_ident'], self.df2proc['hi_redux'])):
            model.setItem(i, 0, QStandardItem(str('RWY ' + ident)))
            item = QStandardItem(str(redux))
            item.setEditable(True)
            model.setItem(i, 1, item)
    
        # Fill lo_ident and lo_redux
        # offset = len(self.df2proc['hi_ident'])
        for j, (ident, redux) in enumerate(zip(self.df2proc['lo_ident'], self.df2proc['lo_redux'])):
            # model.setItem(offset + j, 2, QStandardItem(str('RWY ' + ident)))
            model.setItem(j, 2, QStandardItem(str('RWY ' + ident)))
            item = QStandardItem(str(redux))
            item.setEditable(True)
            # model.setItem(offset + j, 3, item)
            model.setItem(j, 3, item)
            
        model.itemChanged.connect(self.handle_redux_change)
        self.rwymodtable.show()
        
    
    def handle_rwyMod_no(self):
        self.rwyModWidget.hide()
        self.df2proc['hi_redux'] = 0
        self.df2proc['lo_redux'] = 0
        self.save_output_files()
        
    def handle_rwymodtable(self):
        model = self.customTable.model()
    
        hi_count = len(self.df2proc['hi_ident'])
        lo_count = len(self.df2proc['lo_ident'])
    
        # Extract updated hi_redux
        updated_hi_redux = []
        for i in range(hi_count):
            item = model.item(i, 1)
            updated_hi_redux.append(item.text())
    
        # Extract updated lo_redux
        updated_lo_redux = []
        for j in range(lo_count):
            item = model.item(j, 3)
            updated_lo_redux.append(item.text())
    
        # Write back to df2proc
        self.df2proc['hi_redux'] = updated_hi_redux
        self.df2proc['lo_redux'] = updated_lo_redux
    
        print("Updated REDUX values saved to df2proc.")
        self.rwymodtable.hide()
        self.save_output_files()
        
    def set_icao_from_input(self):
        typed_value = self.Add_ICAO_lineEdit.text().strip().upper()
        if len(typed_value) <= 4:
            self.icao = typed_value
            self.Add_ICAO_QWidget.hide()  # Optional: hide after setting
        else:
            # Optional: truncate or show warning
            self.icao = typed_value[:4]   
            
    def on_icao_text_changed(self, text):
        if len(text) == 4:
            self.Add_ICAO_lineEdit.setStyleSheet("""
                QLineEdit {
                    background-color: #2b2b2b;
                    border: 1px solid #00FF00;
                    color: #00FF00;
                    border-radius: 4px;
                    padding: 4px;
                }
                """)
            self.Add_ICAO_button1.show()
        else:
            self.Add_ICAO_lineEdit.setStyleSheet("""
                QLineEdit {
                    background-color: #2b2b2b;
                    border: 1px solid #FF0000;
                    color: #FF0000;
                    border-radius: 4px;
                    padding: 4px;
                }
            """)
    def is_valid_icao(self, icao):
        """Return True if ICAO is valid (not empty or '-')"""
        return bool(icao and icao.strip() != '-')

    def collect_checked_rows(self):
        """Process the checked rows and create output files"""
        model = self.DATABASE_AIRFIELDS_tableView.model()
        if not model:
            return
    
        df_indices = self.get_checked_visible_indices(model)
    
        if df_indices:
            self.df2proc = self.filtered_df.loc[df_indices].reset_index(drop=True)
            print(f"{len(self.df2proc)} Runways selected for processing.")
            self.icao = self.df2proc.icao.iloc[0]
            
            if self.icao == '-':
                self.Add_ICAO_lineEdit.setStyleSheet("""
                                                QLineEdit {
                                                    background-color: #2b2b2b;
                                                    border: 1px solid #FF0000;
                                                    color: #FF0000;
                                                    border-radius: 4px;
                                                    padding: 4px;
                                                }
                                            """)
    
                self.Add_ICAO_QWidget.show()
                return
            
                self.Add_ICAO_lineEdit.setText(self.icao)  # Optional: pre-fill with '-'
                
        else:
            self.df2proc = pd.DataFrame()
            print("No rows selected.")
            
        self.rwyModWidget.show()

    def get_checked_visible_indices(self, model):
        """Get indices of checked and visible rows"""
        df_indices = []
        for row in range(model.rowCount()):
            if not self.DATABASE_AIRFIELDS_tableView.isRowHidden(row):
                checkbox_item = model.item(row, 0)
                if (checkbox_item and 
                    checkbox_item.checkState() == Qt.Checked):
                    df_index = checkbox_item.data(Qt.UserRole)
                    if df_index is not None:
                        df_indices.append(df_index)
        return df_indices

    def process_selected_rows(self, df_indices):
        """Process the selected rows and create output"""
        # Get selected rows from filtered dataframe
        self.df2proc = self.filtered_df.loc[df_indices].reset_index(drop=True)
        
        
        # self.df2proc['redux_hi'] = 0
        # self.df2proc['redux_lo'] = 0
        
        # Print processing information
        print(f"{len(self.df2proc)} Runways selected for processing.")

        
        # Get ICAO code and save files
        self.icao = self.df2proc.icao.iloc[0]
        # print(self.icao)
        
        # Save CSV and create rnway
        self.save_output_files()
        


    def save_output_files(self):
        """Save the processed data to CSV and create runway files"""
        # Save to CSV
        icao_path = os.path.join(os.path.dirname(__file__), '..', '..','RETURNS', self.icao)
        os.makedirs(icao_path, exist_ok=True)

        csv_path = os.path.join(icao_path, f'{self.icao}_CHECKED_RWYS.csv')
        self.df2proc.to_csv(csv_path, index=False)
        
        def both_runways(df2proc: pd.DataFrame):
            """
            Automatically swaps columns that start with 'hi_' and 'lo_' in pairs,
            returning a DataFrame with original and mirrored runway rows.
            """
            # Identify matching 'hi_' and 'lo_' column pairs
            hi_cols = [col for col in df2proc.columns if col.startswith('hi_')]
            lo_cols = [col for col in df2proc.columns if col.startswith('lo_')]

            # Match by suffix (e.g., 'ident', 'wgs_lat') to form swap pairs
            swap_pairs = []
            for hi in hi_cols:
                suffix = hi[3:]  # strip 'hi_'
                lo = f'lo_{suffix}'
                if lo in lo_cols:
                    swap_pairs.append((hi, lo))

            new_rows = []

            for _, row in df2proc.iterrows():
                rwy = row.copy()
                inv_rwy = row.copy()

                for col1, col2 in swap_pairs:
                    inv_rwy[col1], inv_rwy[col2] = row[col2], row[col1]

                new_rows.extend([rwy, inv_rwy])

            return pd.DataFrame(new_rows, columns=df2proc.columns) #returns the new dataframe with all the hi los inveresed to create opposite runway

        self.df2proc = both_runways(self.df2proc)
        # self.df2proc.to_csv(self.df2proc)
        # Create runway file
        makerunway_kml(self.df2proc, self.icao, self.TD_Dist_lineEdit.text(), 
                        self.STP_Dist_lineEdit.text(), self.G_Slope_lineEdit.text(),
                        self.TP_Alt_lineEdit.text(), self.RWY_W_Value_label.text(), self.GA_Spd_lineEdit.text(), self.Dep_pt_lineEdit.text())
        
        makerunway_xml(self.df2proc, self.icao, self.TD_Dist_lineEdit.text(), 
                        self.STP_Dist_lineEdit.text(), self.G_Slope_lineEdit.text(),
                        self.TP_Alt_lineEdit.text(), self.RWY_W_Value_label.text(), self.GA_Spd_lineEdit.text(), self.Dep_pt_lineEdit.text())
        print('Complete')
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
