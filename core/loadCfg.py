#!/usr/bin/env python3
import sys
import shutil
import os
import subprocess
import time
from pathlib import Path
import variables

def loadcfg():
    for item in variables.configs_dir.iterdir():
        if item.is_file():
            try:
                content = item.read_text().strip()
                
                dest_file = variables.sysfs_path / item.name
                dest_file.write_text(content)
                
                print(f"Loaded {item.name} to {dest_file}")
            except Exception as e:
                print(f"Skipped {item.name}: {e}")
