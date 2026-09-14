#!/usr/bin/env python3
"""
Complete Sensex Scalping Strategy Analysis Pipeline
Fetches data, backtests strategies, and generates recommendations
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, description):
    """Run a Python script and handle errors"""
    print(f"\n{'='*70}")
    print(f"▶ {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        if result.returncode != 0:
            print(f"✗ Error running {description}")
            return False
        return True
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("SENSEX SCALPING STRATEGY ANALYZER")
    print("="*70)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check dependencies
    print(f"\n{'='*70}")
    print("STEP 1: Checking Dependencies")
    print(f"{'='*70}\n")
    
    try:
        import yfinance
        import pandas
        import numpy
        print("✓ All dependencies installed")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nInstalling dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      capture_output=True)
        print("✓ Dependencies installed")
    
    # Step 2: Fetch data
    if not run_command(f"{sys.executable} fetch_sensex_data.py", "Fetching Sensex Historical Data"):
        print("✗ Failed to fetch data. Exiting.")
        return
    
    # Step 3: Run backtests
    if not run_command(f"{sys.executable} backtest_strategies.py", "Running Strategy Backtests"):
        print("✗ Failed to run backtests. Exiting.")
        return
    
    # Step 4: Generate visualizations
    if not run_command(f"{sys.executable} generate_visualizations.py", "Generating Performance Charts"):
        print("Skipping visualizations (optional)")
    
    # Step 5: Generate recommendations
    if not run_command(f"{sys.executable} generate_recommendations.py", "Generating Trading Recommendations"):
        print("Skipping recommendations (optional)")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print("\nOutput files generated:")
    print("  • sensex_raw_data.csv - Historical Sensex data")
    print("  • sensex_with_indicators.csv - Data with technical indicators")
    print("  • trades_*.csv - Individual trade details for each strategy")
    print("  • performance_chart.png - Strategy performance visualization")
    print("  • BEST_STRATEGY_REPORT.txt - Final recommendations")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
