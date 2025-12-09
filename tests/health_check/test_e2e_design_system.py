"""
End-to-End Test for Design System
Creates a complete project, generates design system and components, validates everything, then cleans up
"""

import pytest
import os
import asyncio
import tempfile
import shutil
from pathlib import Path

# Import the modules to test
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tools.design_system import (
    GenerateDesignSystemInput,
    generate_design_system
)
from src.tools.javascript_tools import (
    GenerateReactComponentInput,
    generate_react_component
)


class TestEndToEndDesignSystem:
    """Complete end-to-end test of the design system"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """
        Complete workflow test:
        1. Create temporary project
        2. Generate design system
        3. Generate multiple components
        4. Validate all files
        5. Clean up everything
        """
        
        print("\n" + "="*80)
        print("🚀 STARTING END-TO-END DESIGN SYSTEM TEST")
        print("="*80 + "\n")
        
        # Step 1: Create temporary project directory
        print("📁 Step 1: Creating temporary project directory...")
        temp_dir = tempfile.mkdtemp(prefix="e2e_test_")
        print(f"   ✅ Created: {temp_dir}\n")
        
        try:
            # Step 2: Generate Design System
            print("🎨 Step 2: Generating design system...")
            design_params = GenerateDesignSystemInput(
                project_path=temp_dir,
                framework="nextjs",
                include_dark_mode=True,
                include_component_patterns=True,
                include_docs=True
            )
            
            design_result = await generate_design_system(design_params)
            
            assert design_result.success is True, f"Design system generation failed: {design_result.error}"
            print(f"   ✅ Generated {design_result.data['token_count']} design tokens")
            print(f"   ✅ Created {len(design_result.data['generated_files'])} files:")
            for file in design_result.data['generated_files']:
                print(f"      - {os.path.basename(file)}")
            print()
            
            # Step 3: Validate Design System Files
            print("🔍 Step 3: Validating design system files...")
            
            # Check Tailwind config
            tailwind_path = os.path.join(temp_dir, "tailwind.config.js")
            assert os.path.exists(tailwind_path), "Tailwind config not found"
            with open(tailwind_path, 'r') as f:
                tailwind_content = f.read()
            assert "module.exports" in tailwind_content
            assert "darkMode" in tailwind_content
            assert "primary" in tailwind_content
            file_size = os.path.getsize(tailwind_path)
            print(f"   ✅ tailwind.config.js ({file_size} bytes)")
            
            # Check globals.css
            css_path = os.path.join(temp_dir, "src", "app", "globals.css")
            assert os.path.exists(css_path), "globals.css not found"
            with open(css_path, 'r') as f:
                css_content = f.read()
            assert "@tailwind base" in css_content
            assert "--color-primary-500" in css_content
            assert ".btn-primary" in css_content
            assert ".card" in css_content
            file_size = os.path.getsize(css_path)
            print(f"   ✅ globals.css ({file_size} bytes)")
            
            # Check documentation
            docs_path = os.path.join(temp_dir, "DESIGN_SYSTEM.md")
            assert os.path.exists(docs_path), "Documentation not found"
            with open(docs_path, 'r') as f:
                docs_content = f.read()
            assert "# Design System Documentation" in docs_content
            assert "## Component Patterns" in docs_content
            file_size = os.path.getsize(docs_path)
            print(f"   ✅ DESIGN_SYSTEM.md ({file_size} bytes)\n")
            
            # Step 4: Generate Multiple Components
            print("🧩 Step 4: Generating React components...")
            
            components_to_generate = [
                {
                    "name": "HeroSection",
                    "pattern": "hero",
                    "variant": "primary",
                    "description": "Hero section for landing page"
                },
                {
                    "name": "FeatureCard",
                    "pattern": "card",
                    "variant": "interactive",
                    "description": "Feature showcase card"
                },
                {
                    "name": "ContactForm",
                    "pattern": "form",
                    "variant": "primary",
                    "description": "Contact form with validation"
                },
                {
                    "name": "PricingTable",
                    "pattern": "pricing",
                    "variant": "primary",
                    "description": "Pricing table component"
                },
                {
                    "name": "ProductList",
                    "pattern": "list",
                    "variant": "grid",
                    "description": "Product listing grid"
                },
                {
                    "name": "ConfirmModal",
                    "pattern": "modal",
                    "variant": "primary",
                    "description": "Confirmation modal dialog"
                },
                {
                    "name": "PrimaryButton",
                    "pattern": "button",
                    "variant": "primary",
                    "description": "Primary action button"
                },
                {
                    "name": "FeatureShowcase",
                    "pattern": "feature",
                    "variant": "primary",
                    "description": "Feature showcase section"
                }
            ]
            
            generated_components = []
            components_dir = os.path.join(temp_dir, "components")
            
            for comp in components_to_generate:
                params = GenerateReactComponentInput(
                    component_name=comp["name"],
                    component_pattern=comp["pattern"],
                    variant=comp.get("variant", "primary"),
                    styling="tailwind",
                    output_dir=components_dir
                )
                
                result = await generate_react_component(params)
                
                assert result.success is True, f"Failed to generate {comp['name']}: {result.error}"
                
                component_file = result.data["component_file"]
                generated_components.append(component_file)
                
                # Validate component file
                assert os.path.exists(component_file), f"Component file not created: {component_file}"
                
                with open(component_file, 'r') as f:
                    component_content = f.read()
                
                # Check for essential React patterns
                assert "import React" in component_content or "React" in component_content
                assert comp["name"] in component_content
                assert "export default" in component_content
                
                # Check for design system usage
                has_design_classes = (
                    "className" in component_content and (
                        "btn" in component_content or
                        "card" in component_content or
                        "bg-primary" in component_content or
                        "text-" in component_content or
                        "hover:" in component_content or
                        "dark:" in component_content
                    )
                )
                assert has_design_classes, f"Component {comp['name']} doesn't use design system classes"
                
                file_size = os.path.getsize(component_file)
                print(f"   ✅ {comp['name']} ({file_size} bytes) - {comp['description']}")
            
            print(f"\n   📦 Total components generated: {len(generated_components)}\n")
            
            # Step 5: Validate Component Integration
            print("🔗 Step 5: Validating component integration with design system...")
            
            integration_checks = {
                "tailwind_classes": 0,
                "dark_mode_support": 0,
                "responsive_design": 0,
                "accessibility": 0,
                "design_patterns": 0
            }
            
            for comp_file in generated_components:
                with open(comp_file, 'r') as f:
                    content = f.read()
                
                # Check for Tailwind classes
                if "className" in content and any(c in content for c in ["bg-", "text-", "p-", "m-", "rounded", "shadow"]):
                    integration_checks["tailwind_classes"] += 1
                
                # Check for dark mode
                if "dark:" in content:
                    integration_checks["dark_mode_support"] += 1
                
                # Check for responsive design
                if any(bp in content for bp in ["sm:", "md:", "lg:", "xl:"]):
                    integration_checks["responsive_design"] += 1
                
                # Check for accessibility
                if any(a11y in content for a11y in ["aria-", "role=", "alt=", "tabIndex"]):
                    integration_checks["accessibility"] += 1
                
                # Check for design patterns
                if any(pattern in content for pattern in ["btn", "card", "form", "modal"]):
                    integration_checks["design_patterns"] += 1
            
            print(f"   ✅ Components using Tailwind classes: {integration_checks['tailwind_classes']}/{len(generated_components)}")
            print(f"   ✅ Components with dark mode support: {integration_checks['dark_mode_support']}/{len(generated_components)}")
            print(f"   ✅ Components with responsive design: {integration_checks['responsive_design']}/{len(generated_components)}")
            print(f"   ✅ Components with accessibility features: {integration_checks['accessibility']}/{len(generated_components)}")
            print(f"   ✅ Components using design patterns: {integration_checks['design_patterns']}/{len(generated_components)}\n")
            
            # Verify that most components have these features
            assert integration_checks["tailwind_classes"] >= len(generated_components) * 0.7, "Not enough components use Tailwind"
            assert integration_checks["design_patterns"] >= len(generated_components) * 0.7, "Not enough components use design patterns"
            
            # Step 6: Test CSS Module Generation
            print("📦 Step 6: Testing CSS Modules generation...")
            
            css_module_params = GenerateReactComponentInput(
                component_name="StyledCard",
                component_pattern="card",
                styling="css-modules",
                output_dir=components_dir
            )
            
            css_result = await generate_react_component(css_module_params)
            assert css_result.success is True
            
            # Check for CSS module file
            css_module_path = os.path.join(components_dir, "StyledCard.module.css")
            assert os.path.exists(css_module_path), "CSS module not created"
            
            with open(css_module_path, 'r') as f:
                css_module_content = f.read()
            
            # Check for design tokens in CSS module
            assert "--color-" in css_module_content or "var(--" in css_module_content
            
            file_size = os.path.getsize(css_module_path)
            print(f"   ✅ StyledCard.module.css ({file_size} bytes)")
            print(f"   ✅ CSS module uses design tokens\n")
            
            # Step 7: Generate Project Statistics
            print("📊 Step 7: Generating project statistics...")
            
            total_files = 0
            total_size = 0
            file_types = {}
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if not file.startswith('.'):
                        total_files += 1
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                        
                        ext = os.path.splitext(file)[1]
                        file_types[ext] = file_types.get(ext, 0) + 1
            
            print(f"   📁 Total files created: {total_files}")
            print(f"   💾 Total size: {total_size:,} bytes ({total_size / 1024:.2f} KB)")
            print(f"   📑 File types:")
            for ext, count in sorted(file_types.items()):
                print(f"      - {ext or 'no extension'}: {count} files")
            print()
            
            # Step 8: Verify Design System Features
            print("✨ Step 8: Verifying design system features...")
            
            features_verified = {
                "Design Tokens": design_result.data['token_count'] > 200,
                "Dark Mode": "darkMode" in tailwind_content,
                "Component Patterns": ".btn" in css_content and ".card" in css_content,
                "Accessibility": "focus-visible" in css_content,
                "Responsive Design": "@media" in css_content or "sm:" in tailwind_content,
                "Animations": "keyframes" in css_content or "@keyframes" in css_content,
                "Documentation": "## Component Patterns" in docs_content,
                "TypeScript": any(".tsx" in f for f in generated_components)
            }
            
            for feature, verified in features_verified.items():
                status = "✅" if verified else "❌"
                print(f"   {status} {feature}")
            
            # All features should be verified
            assert all(features_verified.values()), f"Some features not verified: {features_verified}"
            print()
            
            # Step 9: Test Summary
            print("📋 Step 9: Test summary...")
            print(f"   ✅ Design system generated successfully")
            print(f"   ✅ {len(generated_components)} components created")
            print(f"   ✅ All files validated")
            print(f"   ✅ Design system features verified")
            print(f"   ✅ Integration tests passed")
            print()
            
            # Final assertions
            assert len(generated_components) >= len(components_to_generate), f"Expected at least {len(components_to_generate)} components"
            assert all(os.path.exists(f) for f in generated_components)
            assert os.path.exists(tailwind_path)
            assert os.path.exists(css_path)
            assert os.path.exists(docs_path)
            
            print("="*80)
            print("🎉 END-TO-END TEST COMPLETED SUCCESSFULLY!")
            print("="*80)
            print()
            print("Summary:")
            print(f"  • Design System: ✅ Generated with {design_result.data['token_count']} tokens")
            print(f"  • Components: ✅ Created {len(generated_components)} components")
            print(f"  • Files: ✅ Total {total_files} files ({total_size / 1024:.2f} KB)")
            print(f"  • Validation: ✅ All checks passed")
            print()
            
        finally:
            # Step 10: Cleanup
            print("🧹 Step 10: Cleaning up temporary files...")
            
            if os.path.exists(temp_dir):
                # List what we're deleting
                files_to_delete = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        files_to_delete.append(os.path.join(root, file))
                
                print(f"   🗑️  Deleting {len(files_to_delete)} files from {temp_dir}")
                
                # Delete the temporary directory
                shutil.rmtree(temp_dir)
                
                # Verify deletion
                assert not os.path.exists(temp_dir), "Cleanup failed - directory still exists"
                
                print(f"   ✅ Cleanup complete - all test files deleted")
            
            print()
            print("="*80)
            print("✨ TEST COMPLETE - ALL FILES CLEANED UP")
            print("="*80)
            print()


# ============================================================================
# Additional End-to-End Tests
# ============================================================================

class TestE2EScenarios:
    """Test specific end-to-end scenarios"""
    
    @pytest.mark.asyncio
    async def test_landing_page_creation(self):
        """Test creating a complete landing page with design system"""
        
        print("\n🏠 Testing landing page creation...")
        
        temp_dir = tempfile.mkdtemp(prefix="landing_page_")
        
        try:
            # Generate design system
            design_params = GenerateDesignSystemInput(
                project_path=temp_dir,
                framework="nextjs",
                include_dark_mode=True,
                include_component_patterns=True,
                include_docs=False  # Skip docs for faster test
            )
            
            design_result = await generate_design_system(design_params)
            assert design_result.success is True
            
            # Generate landing page components
            landing_components = ["Hero", "Features", "Pricing", "Testimonials", "CTA", "Footer"]
            
            for comp_name in landing_components:
                params = GenerateReactComponentInput(
                    component_name=comp_name,
                    component_pattern="feature" if comp_name == "Features" else 
                                    "pricing" if comp_name == "Pricing" else
                                    "hero" if comp_name == "Hero" else "card",
                    styling="tailwind",
                    output_dir=os.path.join(temp_dir, "components")
                )
                
                result = await generate_react_component(params)
                assert result.success is True
                print(f"   ✅ {comp_name} component created")
            
            print(f"   ✅ Landing page complete with {len(landing_components)} sections\n")
            
        finally:
            shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_dashboard_creation(self):
        """Test creating dashboard components with design system"""
        
        print("\n📊 Testing dashboard creation...")
        
        temp_dir = tempfile.mkdtemp(prefix="dashboard_")
        
        try:
            # Generate design system
            design_params = GenerateDesignSystemInput(
                project_path=temp_dir,
                framework="nextjs"
            )
            
            design_result = await generate_design_system(design_params)
            assert design_result.success is True
            
            # Generate dashboard components
            dashboard_components = ["Sidebar", "Header", "StatsCard", "DataTable", "Chart"]
            
            for comp_name in dashboard_components:
                params = GenerateReactComponentInput(
                    component_name=comp_name,
                    component_pattern="card" if "Card" in comp_name else "list",
                    styling="tailwind",
                    output_dir=os.path.join(temp_dir, "components")
                )
                
                result = await generate_react_component(params)
                assert result.success is True
                print(f"   ✅ {comp_name} component created")
            
            print(f"   ✅ Dashboard complete with {len(dashboard_components)} components\n")
            
        finally:
            shutil.rmtree(temp_dir)


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
