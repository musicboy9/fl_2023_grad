#!/bin/bash

export PYTHONPATH=../fl_viewer
python3.7 -m venv ../venv
source ../venv/bin/activate
pip3 install -r ../requirements.txt