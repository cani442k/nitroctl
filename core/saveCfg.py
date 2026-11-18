#!/usr/bin/env python3
import sys
import shutil
import os
import subprocess
import time
from pathlib import Path
import variables

def savecfg():
    variables.configs_dir.mkdir(parents=True, exist_ok=True)
    for item in variables.sysfs_path.iterdir():
        if item.is_file():
            try:
                content = item.read_text().strip()
                
                dest_file = variables.configs_dir / item.name
                dest_file.write_text(content)
                
                print(f"Copied {item.name} to {dest_file}")
            except Exception as e:
                print(f"Skipped {item.name}: {e}")
                
