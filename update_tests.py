"""
Script to update test files to use authenticated_client fixture.
"""
import os
import re

def update_test_file(file_path):
    """Update test file to use authenticated_client fixture."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace function signatures
    content = re.sub(
        r'def test_(\w+)\(self, client: TestClient\):',
        r'def test_\1(self, authenticated_client: TestClient):',
        content
    )
    
    # Replace client.post with headers
    content = re.sub(
        r'client\.post\(\s*"([^"]+)",\s*json=([^,]+),\s*headers=headers\s*\)',
        r'authenticated_client.post("\1", json=\2)',
        content
    )
    
    # Replace client.get with headers
    content = re.sub(
        r'client\.get\(\s*"([^"]+)",\s*headers=headers\s*\)',
        r'authenticated_client.get("\1")',
        content
    )
    
    # Replace client.put with headers
    content = re.sub(
        r'client\.put\(\s*"([^"]+)",\s*json=([^,]+),\s*headers=headers\s*\)',
        r'authenticated_client.put("\1", json=\2)',
        content
    )
    
    # Replace client.delete with headers
    content = re.sub(
        r'client\.delete\(\s*"([^"]+)",\s*headers=headers\s*\)',
        r'authenticated_client.delete("\1")',
        content
    )
    
    # Remove headers = self.get_auth_headers(client) lines
    content = re.sub(
        r'\s*headers = self\.get_auth_headers\(client\)',
        '',
        content
    )
    
    with open(file_path, 'w') as f:
        f.write(content)

# Update test files
update_test_file('tests/unit/test_customers.py')
update_test_file('tests/unit/test_inventory.py')
update_test_file('tests/unit/test_products.py')

print("Test files updated successfully!")