# -*- coding: utf-8 -*-
"""
Created on Sat Nov 15 15:01:28 2025

@author: dukes
"""

import os, sys

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):
        # Running from PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running from source
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)