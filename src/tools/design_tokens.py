"""
Professional Design Tokens
Loads design system tokens from JSON configuration
"""

from typing import Dict, Any
import json
import pathlib


def _load_design_tokens() -> Dict[str, Any]:
    """Load design tokens from JSON configuration"""
    config_dir = pathlib.Path(__file__).parent.parent.parent / "config"
    tokens_file = config_dir / "design-tokens.json"
    
    if not tokens_file.exists():
        return {}  # Return empty if file doesn't exist
    
    with open(tokens_file, 'r', encoding='utf-8') as f:
        return json.load(f)


class DesignTokens:
    """
    Professional design token system (loads from JSON)
    
    Includes:
    - Color system (50-900 scales)
    - Typography (fonts, sizes, weights, line heights)
    - Spacing system
    - Border and radius
    - Shadows and elevation
    - Animations and transitions
    - Breakpoints
    - Z-index scale
    """
    
    def __init__(self):
        """Initialize design tokens by loading from JSON"""
        tokens = _load_design_tokens()
        
        # Load each section from JSON
        self.COLORS = tokens.get("colors", {})
        self.TYPOGRAPHY = tokens.get("typography", {})
        self.SPACING = tokens.get("spacing", {})
        self.BORDERS = tokens.get("borders", {})
        self.SHADOWS = tokens.get("shadows", {})
        self.ANIMATIONS = tokens.get("animations", {})
        self.BREAKPOINTS = tokens.get("breakpoints", {})
        self.Z_INDEX = tokens.get("zIndex", {})
    
    def get_all_tokens(self) -> Dict[str, Any]:
        """Get all design tokens as a dictionary"""
        return {
            "colors": self.COLORS,
            "typography": self.TYPOGRAPHY,
            "spacing": self.SPACING,
            "borders": self.BORDERS,
            "shadows": self.SHADOWS,
            "animations": self.ANIMATIONS,
            "breakpoints": self.BREAKPOINTS,
            "zIndex": self.Z_INDEX,
        }
    
    def count_tokens(self) -> int:
        """Count total number of design tokens"""
        def count_nested(obj):
            count = 0
            if isinstance(obj, dict):
                for value in obj.values():
                    if isinstance(value, (dict, list, tuple)):
                        count += count_nested(value)
                    else:
                        count += 1
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    if isinstance(item, (dict, list, tuple)):
                        count += count_nested(item)
                    else:
                        count += 1
            return count
        
        return count_nested(self.get_all_tokens())


# Create singleton instance
design_tokens = DesignTokens()
