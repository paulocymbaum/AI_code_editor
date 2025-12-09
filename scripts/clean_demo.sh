#!/bin/bash

# Clean Demo Folder and Archive Old Files
# Organizes demo folder by archiving old components

set -e

echo "🧹 Cleaning Demo Folder..."
echo ""

# Create archive directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_DIR="./archived_demos/${TIMESTAMP}"

echo "📦 Archive location: $ARCHIVE_DIR"
echo ""

# Run Python script to clean demo
python3 << 'PYTHON_SCRIPT'
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.page_management import clean_demo_folder, CleanDemoFolderInput

async def main():
    # Get timestamp from environment or generate new one
    timestamp = os.environ.get('TIMESTAMP', datetime.now().strftime('%Y%m%d_%H%M%S'))
    archive_dir = f"./archived_demos/{timestamp}"
    
    print(f"🗑️  Cleaning demo folder...")
    print(f"📦 Archiving to: {archive_dir}")
    print("")
    
    # Keep essential config files and the main components
    keep_patterns = [
        "*.config.*",
        "package*.json",
        "tsconfig.json",
        ".env*",
        "HeroSection.tsx",
        "FeatureCard.tsx",
        "PricingCard.tsx",
        "CTAButton.tsx"
    ]
    
    params = CleanDemoFolderInput(
        demo_dir="./demo",
        keep_patterns=keep_patterns,
        archive_dir=archive_dir
    )
    
    result = await clean_demo_folder(params)
    
    if result.success:
        print("✅ Cleanup complete!")
        print(f"📁 Files removed: {result.data['files_removed']}")
        print(f"📌 Files kept: {result.data['files_kept']}")
        print(f"📦 Archive: {result.data['archive_directory']}")
        print("")
        
        if result.data['files_removed'] > 0:
            print("Removed files:")
            for item in result.data['removed'][:10]:  # Show first 10
                print(f"  - {os.path.basename(item['file'])}")
            
            if result.data['files_removed'] > 10:
                print(f"  ... and {result.data['files_removed'] - 10} more")
    else:
        print(f"❌ Error: {result.error}")
        sys.exit(1)

asyncio.run(main())
PYTHON_SCRIPT

echo ""
echo "✅ Demo folder cleaned!"
echo ""
echo "💡 To restore archived files:"
echo "   cp -r $ARCHIVE_DIR/* ./demo/"
