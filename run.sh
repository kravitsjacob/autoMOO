#!/bin/bash

# Load conda commands
eval "$(conda shell.bash hook)"

# Create conda environment
conda env create -f environment.yml

# Load conda environment
conda activate autoMOO

# Run analysis
python main.py