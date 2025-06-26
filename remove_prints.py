"""
Script to remove print statements from test files.
"""
import re
import os

def remove_prints(file_path):
    """Remove print statements from a file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove print statements
    content = re.sub(r'\s*print\(f"Create response: \{data\}"\)\n', '\n', content)
    
    with open(file_path, 'w') as f:
        f.write(content)

# Files to process
files = [
    'tests/unit/test_inventory.py',
    'tests/unit/test_customers.py',
    'tests/unit/test_products.py'
]

for file in files:
    remove_prints(file)

print("Print statements removed successfully!")