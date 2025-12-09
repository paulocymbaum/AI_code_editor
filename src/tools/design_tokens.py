"""
Professional Design Tokens
Hard-coded design system with 100+ tokens for professional UI/UX
"""

from typing import Dict, Any, List, Tuple


class DesignTokens:
    """
    Professional design token system
    
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
    
    # ============================================================================
    # COLOR SYSTEM
    # ============================================================================
    
    COLORS = {
        # Primary Color (Vibrant Purple/Magenta)
        "primary": {
            "50": "#fdf4ff",
            "100": "#fae8ff",
            "200": "#f5d0fe",
            "300": "#f0abfc",
            "400": "#e879f9",
            "500": "#d946ef",
            "600": "#c026d3",
            "700": "#a21caf",
            "800": "#86198f",
            "900": "#701a75",
            "950": "#4a044e",
        },
        
        # Neutral/Warm Gray Scale
        "neutral": {
            "50": "#fafaf9",
            "100": "#f5f5f4",
            "200": "#e7e5e4",
            "300": "#d6d3d1",
            "400": "#a8a29e",
            "500": "#78716c",
            "600": "#57534e",
            "700": "#44403c",
            "800": "#292524",
            "900": "#1c1917",
            "950": "#0c0a09",
        },
        
        # Success (Vibrant Teal)
        "success": {
            "50": "#f0fdfa",
            "100": "#ccfbf1",
            "200": "#99f6e4",
            "300": "#5eead4",
            "400": "#2dd4bf",
            "500": "#14b8a6",
            "600": "#0d9488",
            "700": "#0f766e",
            "800": "#115e59",
            "900": "#134e4a",
            "light": "#ccfbf1",
            "DEFAULT": "#14b8a6",
            "dark": "#134e4a",
        },
        
        # Warning (Vibrant Orange)
        "warning": {
            "50": "#fff7ed",
            "100": "#ffedd5",
            "200": "#fed7aa",
            "300": "#fdba74",
            "400": "#fb923c",
            "500": "#f97316",
            "600": "#ea580c",
            "700": "#c2410c",
            "800": "#9a3412",
            "900": "#7c2d12",
            "light": "#ffedd5",
            "DEFAULT": "#f97316",
            "dark": "#9a3412",
        },
        
        # Error (Hot Pink/Rose)
        "error": {
            "50": "#fff1f2",
            "100": "#ffe4e6",
            "200": "#fecdd3",
            "300": "#fda4af",
            "400": "#fb7185",
            "500": "#f43f5e",
            "600": "#e11d48",
            "700": "#be123c",
            "800": "#9f1239",
            "900": "#881337",
            "light": "#ffe4e6",
            "DEFAULT": "#f43f5e",
            "dark": "#9f1239",
        },
        
        # Info (Vibrant Indigo)
        "info": {
            "50": "#eef2ff",
            "100": "#e0e7ff",
            "200": "#c7d2fe",
            "300": "#a5b4fc",
            "400": "#818cf8",
            "500": "#6366f1",
            "600": "#4f46e5",
            "700": "#4338ca",
            "800": "#3730a3",
            "900": "#312e81",
            "light": "#e0e7ff",
            "DEFAULT": "#6366f1",
            "dark": "#3730a3",
        },
        
        # Semantic Colors
        "semantic": {
            "background": {"light": "#ffffff", "dark": "#0a0a0a"},
            "foreground": {"light": "#171717", "dark": "#fafafa"},
            "card": {"light": "#ffffff", "dark": "#171717"},
            "card-foreground": {"light": "#171717", "dark": "#fafafa"},
            "border": {"light": "#e5e5e5", "dark": "#404040"},
            "muted": {"light": "#f5f5f5", "dark": "#262626"},
            "muted-foreground": {"light": "#737373", "dark": "#a3a3a3"},
            "accent": {"light": "#f5f5f5", "dark": "#262626"},
            "accent-foreground": {"light": "#171717", "dark": "#fafafa"},
        },
    }
    
    # ============================================================================
    # TYPOGRAPHY
    # ============================================================================
    
    TYPOGRAPHY = {
        "font_families": {
            "sans": ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
            "serif": ["Merriweather", "Georgia", "Times New Roman", "serif"],
            "mono": ["Fira Code", "Consolas", "Monaco", "monospace"],
            "display": ["Poppins", "sans-serif"],
        },
        
        "font_sizes": {
            "xs": ("0.75rem", "1rem"),        # 12px / 16px
            "sm": ("0.875rem", "1.25rem"),    # 14px / 20px
            "base": ("1rem", "1.5rem"),       # 16px / 24px
            "lg": ("1.125rem", "1.75rem"),    # 18px / 28px
            "xl": ("1.25rem", "1.75rem"),     # 20px / 28px
            "2xl": ("1.5rem", "2rem"),        # 24px / 32px
            "3xl": ("1.875rem", "2.25rem"),   # 30px / 36px
            "4xl": ("2.25rem", "2.5rem"),     # 36px / 40px
            "5xl": ("3rem", "1"),             # 48px / 48px
            "6xl": ("3.75rem", "1"),          # 60px / 60px
            "7xl": ("4.5rem", "1"),           # 72px / 72px
            "8xl": ("6rem", "1"),             # 96px / 96px
            "9xl": ("8rem", "1"),             # 128px / 128px
        },
        
        "font_weights": {
            "thin": 100,
            "extralight": 200,
            "light": 300,
            "normal": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700,
            "extrabold": 800,
            "black": 900,
        },
        
        "line_heights": {
            "none": 1,
            "tight": 1.25,
            "snug": 1.375,
            "normal": 1.5,
            "relaxed": 1.625,
            "loose": 2,
        },
        
        "letter_spacing": {
            "tighter": "-0.05em",
            "tight": "-0.025em",
            "normal": "0em",
            "wide": "0.025em",
            "wider": "0.05em",
            "widest": "0.1em",
        },
    }
    
    # ============================================================================
    # SPACING
    # ============================================================================
    
    SPACING = {
        "0": "0",
        "px": "1px",
        "0.5": "0.125rem",   # 2px
        "1": "0.25rem",      # 4px
        "1.5": "0.375rem",   # 6px
        "2": "0.5rem",       # 8px
        "2.5": "0.625rem",   # 10px
        "3": "0.75rem",      # 12px
        "3.5": "0.875rem",   # 14px
        "4": "1rem",         # 16px
        "5": "1.25rem",      # 20px
        "6": "1.5rem",       # 24px
        "7": "1.75rem",      # 28px
        "8": "2rem",         # 32px
        "9": "2.25rem",      # 36px
        "10": "2.5rem",      # 40px
        "11": "2.75rem",     # 44px
        "12": "3rem",        # 48px
        "14": "3.5rem",      # 56px
        "16": "4rem",        # 64px
        "20": "5rem",        # 80px
        "24": "6rem",        # 96px
        "28": "7rem",        # 112px
        "32": "8rem",        # 128px
        "36": "9rem",        # 144px
        "40": "10rem",       # 160px
        "44": "11rem",       # 176px
        "48": "12rem",       # 192px
        "52": "13rem",       # 208px
        "56": "14rem",       # 224px
        "60": "15rem",       # 240px
        "64": "16rem",       # 256px
        "72": "18rem",       # 288px
        "80": "20rem",       # 320px
        "96": "24rem",       # 384px
    }
    
    # ============================================================================
    # BORDERS & RADIUS
    # ============================================================================
    
    BORDERS = {
        "width": {
            "0": "0",
            "DEFAULT": "1px",
            "2": "2px",
            "4": "4px",
            "8": "8px",
        },
        "radius": {
            "none": "0",
            "sm": "0.125rem",     # 2px
            "DEFAULT": "0.25rem", # 4px
            "md": "0.375rem",     # 6px
            "lg": "0.5rem",       # 8px
            "xl": "0.75rem",      # 12px
            "2xl": "1rem",        # 16px
            "3xl": "1.5rem",      # 24px
            "full": "9999px",
        },
    }
    
    # ============================================================================
    # SHADOWS & ELEVATION
    # ============================================================================
    
    SHADOWS = {
        "none": "none",
        "xs": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        "sm": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        "DEFAULT": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
        "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)",
        # Component-specific shadows
        "card": "0 2px 8px rgba(0, 0, 0, 0.08)",
        "card-hover": "0 8px 24px rgba(0, 0, 0, 0.12)",
        "dropdown": "0 4px 12px rgba(0, 0, 0, 0.15)",
        "modal": "0 20px 30px rgba(0, 0, 0, 0.2)",
        "focus": "0 0 0 3px rgba(14, 165, 233, 0.5)",
    }
    
    # ============================================================================
    # ANIMATIONS & TRANSITIONS
    # ============================================================================
    
    ANIMATIONS = {
        "durations": {
            "75": "75ms",
            "100": "100ms",
            "150": "150ms",
            "200": "200ms",
            "250": "250ms",
            "300": "300ms",
            "350": "350ms",
            "500": "500ms",
            "700": "700ms",
            "1000": "1000ms",
        },
        
        "timing_functions": {
            "linear": "linear",
            "ease": "ease",
            "ease-in": "ease-in",
            "ease-out": "ease-out",
            "ease-in-out": "ease-in-out",
            "bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
        },
        
        "keyframes": {
            "fadeIn": {
                "from": {"opacity": "0"},
                "to": {"opacity": "1"},
            },
            "fadeOut": {
                "from": {"opacity": "1"},
                "to": {"opacity": "0"},
            },
            "slideUp": {
                "from": {"transform": "translateY(10px)", "opacity": "0"},
                "to": {"transform": "translateY(0)", "opacity": "1"},
            },
            "slideDown": {
                "from": {"transform": "translateY(-10px)", "opacity": "0"},
                "to": {"transform": "translateY(0)", "opacity": "1"},
            },
            "slideLeft": {
                "from": {"transform": "translateX(10px)", "opacity": "0"},
                "to": {"transform": "translateX(0)", "opacity": "1"},
            },
            "slideRight": {
                "from": {"transform": "translateX(-10px)", "opacity": "0"},
                "to": {"transform": "translateX(0)", "opacity": "1"},
            },
            "scaleUp": {
                "from": {"transform": "scale(0.95)", "opacity": "0"},
                "to": {"transform": "scale(1)", "opacity": "1"},
            },
            "spin": {
                "from": {"transform": "rotate(0deg)"},
                "to": {"transform": "rotate(360deg)"},
            },
            "pulse": {
                "0%, 100%": {"opacity": "1"},
                "50%": {"opacity": "0.5"},
            },
        },
    }
    
    # ============================================================================
    # BREAKPOINTS
    # ============================================================================
    
    BREAKPOINTS = {
        "xs": "0px",
        "sm": "640px",
        "md": "768px",
        "lg": "1024px",
        "xl": "1280px",
        "2xl": "1536px",
    }
    
    # ============================================================================
    # Z-INDEX SCALE
    # ============================================================================
    
    Z_INDEX = {
        "0": 0,
        "10": 10,
        "20": 20,
        "30": 30,
        "40": 40,
        "50": 50,
        "auto": "auto",
        # Component layers
        "dropdown": 1000,
        "sticky": 1020,
        "fixed": 1030,
        "modal-backdrop": 1040,
        "modal": 1050,
        "popover": 1060,
        "tooltip": 1070,
    }
    
    @classmethod
    def get_all_tokens(cls) -> Dict[str, Any]:
        """Get all design tokens as a dictionary"""
        return {
            "colors": cls.COLORS,
            "typography": cls.TYPOGRAPHY,
            "spacing": cls.SPACING,
            "borders": cls.BORDERS,
            "shadows": cls.SHADOWS,
            "animations": cls.ANIMATIONS,
            "breakpoints": cls.BREAKPOINTS,
            "zIndex": cls.Z_INDEX,
        }
    
    @classmethod
    def count_tokens(cls) -> int:
        """Count total number of design tokens"""
        total = 0
        tokens = cls.get_all_tokens()
        
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
        
        return count_nested(tokens)


# Create singleton instance
design_tokens = DesignTokens()
