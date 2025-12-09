"""
Design System Configuration Loader
Handles loading and fallback logic for design system configurations
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json

class DesignSystemConfigLoader:
    """Load design system configuration with intelligent fallback"""
    
    # Priority order for finding config files
    CONFIG_SEARCH_PATHS = [
        "design-system.config.json",           # Project root
        "config/design-system.json",           # Config folder
        "config/design-tokens.json",           # Alt name
        ".design-system.json",                 # Hidden file
        "themes/default.json",                 # Themes folder
    ]
    
    # Fallback to example if no user config found
    FALLBACK_CONFIG = "config/design-system.example.json"
    
    @staticmethod
    def find_config(project_root: str = ".") -> Optional[Path]:
        """
        Find design system config file in project
        
        Search order:
        1. User's custom config files (in priority order)
        2. Fallback to design-system.example.json
        3. Return None if nothing found
        """
        root = Path(project_root)
        
        # Try to find user config
        for config_path in DesignSystemConfigLoader.CONFIG_SEARCH_PATHS:
            full_path = root / config_path
            if full_path.exists():
                return full_path
        
        # Fallback to example
        example_path = root / DesignSystemConfigLoader.FALLBACK_CONFIG
        if example_path.exists():
            return example_path
        
        # No config found
        return None
    
    @staticmethod
    def load_config(
        project_root: str = ".",
        config_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load design system configuration
        
        Args:
            project_root: Project root directory
            config_path: Specific config file (optional)
        
        Returns:
            Dict containing design system configuration
        
        Raises:
            FileNotFoundError: If no config found
            json.JSONDecodeError: If config is invalid JSON
        """
        if config_path:
            # Use specified config
            path = Path(project_root) / config_path
            if not path.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
        else:
            # Auto-discover config
            path = DesignSystemConfigLoader.find_config(project_root)
            if not path:
                raise FileNotFoundError(
                    f"No design system config found. Searched:\n" +
                    "\n".join(f"  - {p}" for p in DesignSystemConfigLoader.CONFIG_SEARCH_PATHS) +
                    f"\n  - {DesignSystemConfigLoader.FALLBACK_CONFIG}"
                )
        
        # Load and parse JSON
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Add metadata about source
        config['_meta'] = {
            'source': str(path),
            'is_example': path.name == 'design-system.example.json'
        }
        
        return config
    
    @staticmethod
    def load_config_or_default(project_root: str = ".") -> Dict[str, Any]:
        """
        Load config with automatic fallback to example
        Never fails - returns example if nothing else found
        """
        try:
            return DesignSystemConfigLoader.load_config(project_root)
        except FileNotFoundError:
            # Last resort: return hardcoded minimal config
            return {
                "version": "1.0.0",
                "name": "Default Design System",
                "description": "Fallback design system configuration",
                "_meta": {
                    "source": "hardcoded",
                    "is_example": True
                },
                "colors": {
                    "primary": {"500": "#3b82f6"},
                    "neutral": {"500": "#737373"}
                },
                "generation": {
                    "output": {
                        "tailwindConfig": True,
                        "globalCSS": True
                    }
                }
            }


# Usage example
if __name__ == "__main__":
    # Example 1: Auto-discover config
    config = DesignSystemConfigLoader.load_config_or_default()
    print(f"Loaded: {config['name']}")
    print(f"Source: {config['_meta']['source']}")
    
    # Example 2: Specific config
    try:
        config = DesignSystemConfigLoader.load_config(
            config_path="config/brand-tokens.json"
        )
    except FileNotFoundError as e:
        print(f"Not found: {e}")
