"""
Comprehensive test suite for Design System tools
Tests token generation, file creation, and component integration
"""

import pytest
import os
import json
import asyncio
from pathlib import Path
import tempfile
import shutil

# Import the modules to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.design_tokens import DesignTokens
from src.tools.design_system import (
    DesignSystemGenerator,
    GenerateDesignSystemInput,
    generate_design_system
)
from src.tools.javascript_tools import (
    GenerateReactComponentInput,
    generate_react_component
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def design_tokens():
    """Create a DesignTokens instance"""
    return DesignTokens()


@pytest.fixture
def design_system_generator(design_tokens):
    """Create a DesignSystemGenerator instance"""
    return DesignSystemGenerator(design_tokens)


# ============================================================================
# Design Tokens Tests
# ============================================================================

class TestDesignTokens:
    """Test the DesignTokens class"""
    
    def test_tokens_exist(self, design_tokens):
        """Test that all token categories exist"""
        assert hasattr(design_tokens, 'COLORS')
        assert hasattr(design_tokens, 'TYPOGRAPHY')
        assert hasattr(design_tokens, 'SPACING')
        assert hasattr(design_tokens, 'BORDERS')
        assert hasattr(design_tokens, 'SHADOWS')
        assert hasattr(design_tokens, 'ANIMATIONS')
        assert hasattr(design_tokens, 'BREAKPOINTS')
        assert hasattr(design_tokens, 'Z_INDEX')
    
    def test_color_scales(self, design_tokens):
        """Test that color scales have proper shades"""
        colors = design_tokens.COLORS
        
        # Test primary color scale
        assert "primary" in colors
        for shade in ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]:
            assert shade in colors["primary"], f"Missing shade {shade} in primary"
        
        # Test semantic colors
        assert "semantic" in colors
        assert "background" in colors["semantic"]
        assert "foreground" in colors["semantic"]
        assert "border" in colors["semantic"]
    
    def test_typography_structure(self, design_tokens):
        """Test typography tokens structure"""
        typo = design_tokens.TYPOGRAPHY
        
        assert "font_families" in typo
        assert "sans" in typo["font_families"]
        assert "serif" in typo["font_families"]
        assert "mono" in typo["font_families"]
        
        assert "font_sizes" in typo
        assert "base" in typo["font_sizes"]
        
        assert "font_weights" in typo
        assert "normal" in typo["font_weights"]
        assert "bold" in typo["font_weights"]
    
    def test_spacing_scale(self, design_tokens):
        """Test spacing scale"""
        spacing = design_tokens.SPACING
        
        # Test common spacing values
        for value in ["0", "1", "2", "4", "8", "16", "24", "32"]:
            assert value in spacing, f"Missing spacing value {value}"
    
    def test_shadows(self, design_tokens):
        """Test shadow tokens"""
        shadows = design_tokens.SHADOWS
        
        assert "sm" in shadows
        assert "md" in shadows
        assert "lg" in shadows
        assert "xl" in shadows
        assert "none" in shadows
    
    def test_animations(self, design_tokens):
        """Test animation tokens"""
        animations = design_tokens.ANIMATIONS
        
        assert "durations" in animations
        assert "timing_functions" in animations
        assert "keyframes" in animations
        
        # Test specific durations
        assert "200" in animations["durations"]
        assert "300" in animations["durations"]
    
    def test_breakpoints(self, design_tokens):
        """Test responsive breakpoints"""
        breakpoints = design_tokens.BREAKPOINTS
        
        assert "sm" in breakpoints
        assert "md" in breakpoints
        assert "lg" in breakpoints
        assert "xl" in breakpoints
    
    def test_token_count(self, design_tokens):
        """Test that token count is accurate"""
        count = design_tokens.count_tokens()
        assert count > 200, "Should have at least 200 tokens"
        assert count < 500, "Token count seems too high"
    
    def test_get_all_tokens(self, design_tokens):
        """Test get_all_tokens method"""
        all_tokens = design_tokens.get_all_tokens()
        
        assert isinstance(all_tokens, dict)
        assert "colors" in all_tokens
        assert "typography" in all_tokens
        assert "spacing" in all_tokens


# ============================================================================
# Design System Generator Tests
# ============================================================================

class TestDesignSystemGenerator:
    """Test the DesignSystemGenerator class"""
    
    def test_generator_initialization(self, design_system_generator):
        """Test that generator initializes properly"""
        assert design_system_generator.tokens is not None
    
    def test_generate_tailwind_config(self, design_system_generator):
        """Test Tailwind config generation"""
        config = design_system_generator.generate_tailwind_config(include_dark_mode=True)
        
        assert isinstance(config, str)
        assert "module.exports" in config
        assert "darkMode" in config
        assert "colors" in config
        assert "primary" in config
        assert "fontFamily" in config
    
    def test_generate_tailwind_config_no_dark_mode(self, design_system_generator):
        """Test Tailwind config without dark mode"""
        config = design_system_generator.generate_tailwind_config(include_dark_mode=False)
        
        assert isinstance(config, str)
        assert '"darkMode": false' in config or '"darkMode": False' in config
    
    def test_generate_global_css(self, design_system_generator):
        """Test global CSS generation"""
        css = design_system_generator.generate_global_css(
            include_dark_mode=True,
            include_components=True
        )
        
        assert isinstance(css, str)
        assert "@tailwind base" in css
        assert "@tailwind components" in css
        assert "@tailwind utilities" in css
        assert "--color-primary-500" in css
        assert ".btn" in css
        assert ".card" in css
    
    def test_generate_global_css_no_components(self, design_system_generator):
        """Test CSS generation without component patterns"""
        css = design_system_generator.generate_global_css(
            include_dark_mode=True,
            include_components=False
        )
        
        assert isinstance(css, str)
        assert "@tailwind" in css
        assert "--color-primary-500" in css
        # Should not include component patterns
        assert ".btn-primary" not in css
    
    def test_dark_mode_in_css(self, design_system_generator):
        """Test dark mode variables in CSS"""
        css = design_system_generator.generate_global_css(include_dark_mode=True)
        
        assert ".dark" in css
        assert "dark:bg-neutral" in css or "--color-background" in css
    
    def test_generate_documentation(self, design_system_generator):
        """Test documentation generation"""
        docs = design_system_generator.generate_documentation()
        
        assert isinstance(docs, str)
        assert "# Design System Documentation" in docs
        assert "## Design Tokens" in docs
        assert "## Component Patterns" in docs
        assert "## Accessibility" in docs
        assert "### Buttons" in docs
        assert "### Cards" in docs


# ============================================================================
# Full Design System Generation Tests
# ============================================================================

class TestGenerateDesignSystem:
    """Test the full design system generation process"""
    
    @pytest.mark.asyncio
    async def test_generate_design_system_success(self, temp_project_dir):
        """Test successful design system generation"""
        params = GenerateDesignSystemInput(
            project_path=temp_project_dir,
            framework="nextjs",
            include_dark_mode=True,
            include_component_patterns=True,
            include_docs=True
        )
        
        result = await generate_design_system(params)
        
        assert result.success is True
        assert "generated_files" in result.data
        assert "token_count" in result.data
        assert result.data["token_count"] > 200
    
    @pytest.mark.asyncio
    async def test_files_created(self, temp_project_dir):
        """Test that all expected files are created"""
        params = GenerateDesignSystemInput(
            project_path=temp_project_dir,
            framework="nextjs",
            include_dark_mode=True,
            include_component_patterns=True,
            include_docs=True
        )
        
        result = await generate_design_system(params)
        
        assert result.success is True
        
        # Check Tailwind config
        tailwind_config_path = os.path.join(temp_project_dir, "tailwind.config.js")
        assert os.path.exists(tailwind_config_path)
        
        # Check globals.css
        css_path = os.path.join(temp_project_dir, "src", "app", "globals.css")
        assert os.path.exists(css_path)
        
        # Check documentation
        docs_path = os.path.join(temp_project_dir, "DESIGN_SYSTEM.md")
        assert os.path.exists(docs_path)
    
    @pytest.mark.asyncio
    async def test_tailwind_config_content(self, temp_project_dir):
        """Test that generated Tailwind config has valid content"""
        params = GenerateDesignSystemInput(
            project_path=temp_project_dir,
            framework="nextjs"
        )
        
        result = await generate_design_system(params)
        assert result.success is True
        
        tailwind_config_path = os.path.join(temp_project_dir, "tailwind.config.js")
        with open(tailwind_config_path, 'r') as f:
            content = f.read()
        
        assert "module.exports" in content
        assert "content" in content
        assert "theme" in content
        assert "extend" in content
    
    @pytest.mark.asyncio
    async def test_css_content(self, temp_project_dir):
        """Test that generated CSS has valid content"""
        params = GenerateDesignSystemInput(
            project_path=temp_project_dir,
            framework="nextjs"
        )
        
        result = await generate_design_system(params)
        assert result.success is True
        
        css_path = os.path.join(temp_project_dir, "src", "app", "globals.css")
        with open(css_path, 'r') as f:
            content = f.read()
        
        assert "@tailwind base" in content
        assert ":root {" in content
        assert "--color-" in content
        assert "@layer" in content
    
    @pytest.mark.asyncio
    async def test_invalid_project_path(self):
        """Test that invalid project path returns error"""
        params = GenerateDesignSystemInput(
            project_path="/nonexistent/path/to/project"
        )
        
        result = await generate_design_system(params)
        
        assert result.success is False
        assert result.error is not None
        assert "does not exist" in result.error


# ============================================================================
# Component Generation Integration Tests
# ============================================================================

class TestComponentGenerationIntegration:
    """Test that component generation works with design system"""
    
    @pytest.mark.asyncio
    async def test_generate_button_component(self, temp_project_dir):
        """Test generating a button component with design system"""
        params = GenerateReactComponentInput(
            component_name="MyButton",
            component_pattern="button",
            variant="primary",
            styling="tailwind",
            output_dir=temp_project_dir
        )
        
        result = await generate_react_component(params)
        
        assert result.success is True
        assert "component_file" in result.data
    
    @pytest.mark.asyncio
    async def test_generated_component_has_design_classes(self, temp_project_dir):
        """Test that generated component uses design system classes"""
        params = GenerateReactComponentInput(
            component_name="TestButton",
            component_pattern="button",
            variant="primary",
            styling="tailwind",
            output_dir=temp_project_dir
        )
        
        result = await generate_react_component(params)
        assert result.success is True
        
        component_file = result.data["component_file"]
        with open(component_file, 'r') as f:
            content = f.read()
        
        # Should have design system classes
        assert "bg-primary-600" in content or "btn-primary" in content
        # Check for design system patterns (button uses class from globals.css)
        assert "btn" in content or "bg-primary" in content
    
    @pytest.mark.asyncio
    async def test_generate_multiple_patterns(self, temp_project_dir):
        """Test generating multiple component patterns"""
        patterns = ["button", "card", "form", "modal"]
        
        for pattern in patterns:
            params = GenerateReactComponentInput(
                component_name=f"Test{pattern.capitalize()}",
                component_pattern=pattern,
                styling="tailwind",
                output_dir=temp_project_dir
            )
            
            result = await generate_react_component(params)
            assert result.success is True, f"Failed to generate {pattern} component"


# ============================================================================
# Accessibility Tests
# ============================================================================

class TestAccessibility:
    """Test accessibility features in design system"""
    
    def test_focus_visible_styles(self, design_system_generator):
        """Test that focus-visible styles are included"""
        css = design_system_generator.generate_global_css()
        
        assert "focus-visible" in css
        assert "focus-visible-ring" in css
    
    def test_reduced_motion_support(self, design_system_generator):
        """Test that reduced motion media query is included"""
        css = design_system_generator.generate_global_css()
        
        assert "prefers-reduced-motion" in css
    
    def test_aria_support_in_docs(self, design_system_generator):
        """Test that documentation mentions ARIA"""
        docs = design_system_generator.generate_documentation()
        
        assert "aria-" in docs.lower() or "ARIA" in docs or "accessibility" in docs.lower()
    
    def test_semantic_html_in_docs(self, design_system_generator):
        """Test that documentation mentions semantic HTML"""
        docs = design_system_generator.generate_documentation()
        
        assert "semantic" in docs.lower()


# ============================================================================
# Dark Mode Tests
# ============================================================================

class TestDarkMode:
    """Test dark mode functionality"""
    
    def test_dark_mode_class(self, design_system_generator):
        """Test that dark mode uses class strategy"""
        config = design_system_generator.generate_tailwind_config(include_dark_mode=True)
        
        assert '"darkMode": "class"' in config
    
    def test_dark_mode_variants_in_css(self, design_system_generator):
        """Test that CSS includes dark mode variants"""
        css = design_system_generator.generate_global_css(include_dark_mode=True)
        
        assert ".dark" in css
        assert "dark:" in css
    
    def test_dark_mode_colors(self, design_system_generator):
        """Test that dark mode has color overrides"""
        css = design_system_generator.generate_global_css(include_dark_mode=True)
        
        # Should have dark mode background/surface colors
        assert "--color-background" in css or "dark:bg-" in css


# ============================================================================
# Performance and Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_generate_without_docs(self, temp_project_dir):
        """Test generation without documentation"""
        params = GenerateDesignSystemInput(
            project_path=temp_project_dir,
            include_docs=False
        )
        
        result = await generate_design_system(params)
        assert result.success is True
        
        # Docs should not be created
        docs_path = os.path.join(temp_project_dir, "DESIGN_SYSTEM.md")
        assert not os.path.exists(docs_path)
    
    @pytest.mark.asyncio
    async def test_generate_without_components(self, temp_project_dir):
        """Test generation without component patterns"""
        params = GenerateDesignSystemInput(
            project_path=temp_project_dir,
            include_component_patterns=False
        )
        
        result = await generate_design_system(params)
        assert result.success is True
        
        css_path = os.path.join(temp_project_dir, "src", "app", "globals.css")
        with open(css_path, 'r') as f:
            content = f.read()
        
        # Should not have .btn-primary class
        assert ".btn-primary" not in content
    
    def test_token_count_consistency(self, design_tokens):
        """Test that token count is consistent across calls"""
        count1 = design_tokens.count_tokens()
        count2 = design_tokens.count_tokens()
        
        assert count1 == count2


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
