#!/usr/bin/env python3
"""
Create a run_tbeauty.sh script that reads from .env file.
"""
import os
import shutil

def create_run_script():
    """Create run_tbeauty.sh from the example template."""
    example_file = "run_tbeauty.sh.example"
    target_file = "run_tbeauty.sh"
    
    if not os.path.exists(example_file):
        print(f"❌ {example_file} not found!")
        return False
    
    # Copy the example to the actual script
    shutil.copy2(example_file, target_file)
    
    # Make it executable
    os.chmod(target_file, 0o755)
    
    print(f"✅ Created {target_file}")
    print(f"✅ Made {target_file} executable")
    print(f"\n💡 You can now run: ./{target_file}")
    print(f"   This will automatically load your .env file configuration")
    
    return True

if __name__ == "__main__":
    print("🚀 Creating run_tbeauty.sh script...")
    
    if create_run_script():
        print("🎉 Script created successfully!")
    else:
        print("❌ Failed to create script")