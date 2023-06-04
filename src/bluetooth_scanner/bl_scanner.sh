#!/bin/bash
stdbuf -oL bluetoothctl scan on > file.test
python3 bl_scanner.py $(hcitool dev | cut -sf3)
