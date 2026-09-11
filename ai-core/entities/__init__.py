"""
Entities processing and relationship detection module.
"""

from .models import EntityBase, PlatformCategory
from .relationships import detect_entity_relationships

__all__ = ["EntityBase", "PlatformCategory", "detect_entity_relationships"]
