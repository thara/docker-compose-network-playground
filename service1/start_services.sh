#!/bin/bash

# Start private app in background
python private_app.py &

# Start public app in foreground
python app.py