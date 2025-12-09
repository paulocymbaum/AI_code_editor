#!/bin/bash

# Auto-Generate Demo Page with Components
# This script demonstrates how to use the new page management tools

set -e

echo "🎨 Auto-Generating Demo Page with Design System Components..."
echo ""

# Run Python script to generate page with components
python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.page_management import generate_page_with_components, GeneratePageWithComponentsInput

async def main():
    print("📦 Generating components and page...")
    print("")
    
    # Define components to generate
    components = [
        {
            "name": "ProductCard",
            "pattern": "card",
            "variant": "primary",
            "props_data": {
                "title": "Product Name",
                "price": 99.99,
                "image": "https://via.placeholder.com/300"
            }
        },
        {
            "name": "TestimonialCard",
            "pattern": "card",
            "variant": "secondary",
            "props_data": {
                "author": "John Doe",
                "role": "CEO",
                "content": "Amazing product!"
            }
        },
        {
            "name": "NewsletterForm",
            "pattern": "form",
            "variant": "primary",
            "props_data": {}
        }
    ]
    
    # Generate page with components
    params = GeneratePageWithComponentsInput(
        page_name="showcase",
        page_path="./demo/src/app/showcase/page.tsx",
        components=components,
        title="Component Showcase",
        description="Explore our beautiful component library"
    )
    
    result = await generate_page_with_components(params)
    
    if result.success:
        print("✅ Success!")
        print(f"📄 Page created: {result.data['page_path']}")
        print(f"🎨 Components generated: {', '.join(result.data['components'])}")
        print("")
        print("🚀 View at: http://localhost:3000/showcase")
    else:
        print(f"❌ Error: {result.error}")
        sys.exit(1)

asyncio.run(main())
PYTHON_SCRIPT

echo ""
echo "✅ Demo page generated!"
echo ""
echo "🚀 To view:"
echo "   cd demo && npm run dev"
echo "   Open http://localhost:3000/showcase"
