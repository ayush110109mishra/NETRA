"""
Pytest configuration for NETRA Intelligence Core.
Adds ai-core to sys.path so test modules can import components cleanly.
"""

import sys
from pathlib import Path

ai_core_dir = Path(__file__).resolve().parent.parent
if str(ai_core_dir) not in sys.path:
    sys.path.insert(0, str(ai_core_dir))
