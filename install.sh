#!/bin/bash

virtualenv venv
source venv/bin/activate
pip install --upgrade pip
cd app
pip install -r requirements/default.txt
pip install -e .
