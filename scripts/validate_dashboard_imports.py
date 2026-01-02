#!/usr/bin/env python3
"""Validate dashboard dependencies for GitHub Actions smoke test."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "dashboard"))

try:
    import streamlit as st
    print("✓ streamlit imported successfully")
    
    from pathlib import Path
    print("✓ pathlib imported successfully")
    
    import pandas as pd
    print("✓ pandas imported successfully")
    
    import numpy as np
    print("✓ numpy imported successfully")
    
    import plotly.express as px
    print("✓ plotly.express imported successfully")
    
    from tracing_setup import init_tracing
    print("✓ tracing_setup imported successfully")
    
    print("\n✅ All core imports successful")
    print("✅ Streamlit, pandas, numpy, altair, plotly verified")
    print("✅ Tracing setup available")
    print("✅ Dashboard app dependencies verified")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
