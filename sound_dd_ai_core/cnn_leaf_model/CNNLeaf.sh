#!/bin/bash
# Enterprise Constraint: Execution via Shell Script
# Usage: ./CNNLeaf.sh <audio_file_path>

# Ensure python path is set
export PYTHONPATH=$PYTHONPATH:.

# Execute Python Inference Module
python3 -m cnn_leaf_model.inference "$1"