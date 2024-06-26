import os
import sys

import pytest
import asyncio
import logging
from typing import AsyncIterator, Iterator





logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(f"{cwd}/.."))

# the following import only works after sys.path is updated




