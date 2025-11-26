# -*- coding: utf-8 -*-
"""
Dialogs Registry - Central registry of dialogs for ATOL application.
Maps dialog keys to (ui_file, result_func, init_func) tuples.
"""

import re
from resource_loader import ResourceLoader

# Initialize loader once
loader = ResourceLoader()


def collect_name(dialog):
    """Return the entered name from NameDialog."""
    return {"name": dialog.lineEditName.text()}


def collect_settings(dialog):
    """Return settings values from SettingsDialog."""
    return {
        "theme": dialog.comboBoxTheme.currentText(),
        "autosave": dialog.checkBoxAutosave.isChecked()
    }


def init_table(dialog, params):
    """Populate QTableWidget with column names from params."""
    columns = params.get("columns", [])
    dialog.tableWidget.setColumnCount(len(columns))
    dialog.tableWidget.setHorizontalHeaderLabels(columns)


def init_combo(dialog, params):
    """Populate QComboBox with values from params."""
    values = params.get("values", [])
    dialog.comboBoxOptions.clear()
    dialog.comboBoxOptions.addItems(values)


def init_validated_lineedits(dialog, params):
    """
    Initialize QLineEdits with default '-' and attach multi-condition validators.
    params: dict with keys {"targets": [
        {"name": "lineEdit1", "rules": [{"type": "length", "value": 4}]},
        {"name": "lineEdit2", "rules": [{"type": "regex", "pattern": r"^[A-Z]{3}$"}]},
        {"name": "lineEdit3", "rules": [{"type": "range", "min": 10, "max": 99}]}
    ]}
    """
    for target in params.get("targets", []):
        obj_name = target["name"]
        rules = target.get("rules", [])
        le = getattr(dialog, obj_name, None)
        if le:
            le.setText("-")  # default value
            le.textChanged.connect(lambda text, le=le, rules=rules: validate_input(le, text, rules))


def validate_input(le, text, rules):
    """
    Apply multiple validation rules to a QLineEdit.
    - length: exact length match
    - regex: pattern match
    - range: numeric range
    """
    valid = True
    for rule in rules:
        if rule["type"] == "length":
            if len(text) != rule["value"]:
                valid = False
        elif rule["type"] == "regex":
            if not re.match(rule["pattern"], text):
                valid = False
        elif rule["type"] == "range":
            try:
                num = int(text)
                if num < rule["min"] or num > rule["max"]:
                    valid = False
            except ValueError:
                valid = False

    # Update border color based on validity
    le.setStyleSheet("border: 2px solid green;" if valid else "border: 2px solid red;")


# Central dialog registry
# Format: key -> (ui_file, result_func, init_func)
# ui_file can be a filename (resolved by DialogFactory using ResourceLoader)
# or an absolute path
REGISTRY = {
    "name": (
        "NameDialog.ui",
        collect_name,
        None
    ),
    "settings": (
        "SettingsDialog.ui",
        collect_settings,
        None
    ),
    "table": (
        "TableDialog.ui",
        lambda d: {},
        init_table
    ),
    "combo": (
        "ComboDialog.ui",
        lambda d: {"choice": d.comboBoxOptions.currentText()},
        init_combo
    ),
    "validated": (
        "ValidatedDialog.ui",
        lambda d: {
            "values": [
                d.lineEdit1.text(),
                d.lineEdit2.text(),
                d.lineEdit3.text()
            ]
        },
        init_validated_lineedits
    ),
}
