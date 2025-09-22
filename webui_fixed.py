#!/usr/bin/env python3
"""
Vietnamese AI Dubbing - Web UI với Gradio
Giao diện web đơn giản cho việc lồng tiếng video
"""

import gradio as gr
import os
from pathlib import Path
from main import VietnameseAIDubbing
from config.settings import settings
from modules.translator import translator
from modules.text_to_speech import text_to_speech
import logging

# Ensure logging is configured for web UI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logger.info("Web UI started - testing logging")
print("=== WEB UI LOG TEST ===")

# Khởi tạo dubbing instance
dubbing = VietnameseAIDubbing()
logger.info("VietnameseAIDubbing instance created")