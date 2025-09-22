#!/usr/bin/env python3
"""
Wrapper script to run web UI with separate logging
"""

import os

# Set environment variable for separate log file
os.environ['LOG_FILENAME'] = 'webui_dubbing.log'

# Import webui and run main
import webui
webui.main()