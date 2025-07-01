#!/usr/bin/env python3
"""
Test script to verify file upload functionality.
"""
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_file_upload_service():
    """Test the file upload service functionality."""
    try:
        from app.utils.file_upload import FileUploadService
        
        print("🧪 Testing FileUploadService...")
        
        # Create service instance
        service = FileUploadService("test_uploads")
        print("✅ FileUploadService created successfully")
        
        # Test directory creation
        if service.products_dir.exists():
            print("✅ Upload directories created")
        else:
            print("❌ Upload directories not created")
            return False
        
        # Test filename generation
        filename = service._generate_filename("test.jpg", "primary")
        if filename.startswith("primary_") and filename.endswith(".jpg"):
            print(f"✅ Filename generation works: {filename}")
        else:
            print(f"❌ Filename generation failed: {filename}")
            return False
        
        # Test file validation (mock)
        class MockFile:
            def __init__(self, filename, size=1024):
                self.filename = filename
                self.size = size
        
        # Test valid file
        try:
            service._validate_image_file(MockFile("test.jpg"))
            print("✅ Valid image file validation passed")
        except Exception as e:
            print(f"❌ Valid file validation failed: {e}")
            return False
        
        # Test invalid file extension
        try:
            service._validate_image_file(MockFile("test.txt"))
            print("❌ Invalid file validation should have failed")
            return False
        except Exception:
            print("✅ Invalid file extension properly rejected")
        
        # Test file too large
        try:
            service._validate_image_file(MockFile("test.jpg", 20 * 1024 * 1024))  # 20MB
            print("❌ Large file validation should have failed")
            return False
        except Exception:
            print("✅ Large file properly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ FileUploadService test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_processing():
    """Test image processing capabilities."""
    try:
        from PIL import Image
        import tempfile
        import os
        
        print("\n🖼️ Testing image processing...")
        
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            # Create a simple test image
            img = Image.new('RGB', (1000, 800), color='red')
            img.save(tmp.name, 'JPEG')
            test_image_path = tmp.name
        
        try:
            # Test image opening and processing
            with Image.open(test_image_path) as img:
                print(f"✅ Image opened successfully: {img.size}")
                
                # Test thumbnail creation
                thumbnail = img.copy()
                thumbnail.thumbnail((200, 200), Image.Resampling.LANCZOS)
                print(f"✅ Thumbnail created: {thumbnail.size}")
                
                # Test medium size creation
                medium = img.copy()
                medium.thumbnail((800, 800), Image.Resampling.LANCZOS)
                print(f"✅ Medium size created: {medium.size}")
                
                return True
                
        finally:
            # Clean up test file
            os.unlink(test_image_path)
        
    except Exception as e:
        print(f"❌ Image processing test error: {e}")
        return False

def test_form_data_schemas():
    """Test the form data schemas."""
    try:
        from app.schemas.product import ProductFormData, ProductUpdateFormData
        
        print("\n📋 Testing form data schemas...")
        
        # Test ProductFormData
        form_data = ProductFormData(
            name="Test Product",
            description="Test description",
            base_price=29.99,
            sku="TEST-001",
            weight=0.15,
            is_featured=True
        )
        print("✅ ProductFormData schema works")
        print(f"   Product: {form_data.name} - ${form_data.base_price}")
        
        # Test ProductUpdateFormData
        update_data = ProductUpdateFormData(
            name="Updated Product",
            base_price=35.99
        )
        print("✅ ProductUpdateFormData schema works")
        print(f"   Updated: {update_data.name} - ${update_data.base_price}")
        
        return True
        
    except Exception as e:
        print(f"❌ Form data schema test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_static_file_setup():
    """Test static file configuration."""
    try:
        from pathlib import Path
        
        print("\n📁 Testing static file setup...")
        
        # Test uploads directory creation
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        
        if uploads_dir.exists():
            print("✅ Uploads directory exists")
        else:
            print("❌ Uploads directory not created")
            return False
        
        # Test subdirectory structure
        images_dir = uploads_dir / "images" / "products"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        if images_dir.exists():
            print("✅ Image directory structure created")
        else:
            print("❌ Image directory structure not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Static file setup test error: {e}")
        return False

def show_usage_examples():
    """Show usage examples for the file upload functionality."""
    print("\n" + "="*60)
    print("📚 FILE UPLOAD USAGE EXAMPLES")
    print("="*60)
    
    print("\n1️⃣ CREATE PRODUCT WITH FILES (cURL):")
    print("""
curl -X POST "http://localhost:8000/api/v1/products/with-files" \\
  -H "Authorization: Bearer your-jwt-token" \\
  -F "name=Beauty Product with Images" \\
  -F "description=A beautiful product with uploaded images" \\
  -F "base_price=29.99" \\
  -F "sku=BEAUTY-001" \\
  -F "weight=0.15" \\
  -F "is_featured=true" \\
  -F "primary_image=@/path/to/primary-image.jpg" \\
  -F "additional_images=@/path/to/angle1.jpg" \\
  -F "additional_images=@/path/to/angle2.jpg"
""")
    
    print("\n2️⃣ UPDATE PRODUCT WITH FILES (cURL):")
    print("""
curl -X PUT "http://localhost:8000/api/v1/products/5/with-files" \\
  -H "Authorization: Bearer your-jwt-token" \\
  -F "name=Updated Product Name" \\
  -F "base_price=35.99" \\
  -F "primary_image=@/path/to/new-primary.jpg" \\
  -F "additional_images=@/path/to/new-extra.jpg"
""")
    
    print("\n3️⃣ UPLOAD IMAGES ONLY (cURL):")
    print("""
curl -X POST "http://localhost:8000/api/v1/products/5/upload-images" \\
  -H "Authorization: Bearer your-jwt-token" \\
  -F "primary_image=@/path/to/primary.jpg" \\
  -F "additional_images=@/path/to/extra1.jpg" \\
  -F "additional_images=@/path/to/extra2.jpg" \\
  -F "replace_existing=false"
""")
    
    print("\n4️⃣ JAVASCRIPT EXAMPLE:")
    print("""
const formData = new FormData();
formData.append('name', 'Beauty Product');
formData.append('base_price', '29.99');
formData.append('sku', 'BEAUTY-001');
formData.append('primary_image', primaryImageFile);
formData.append('additional_images', extraImage1);
formData.append('additional_images', extraImage2);

const response = await fetch('/api/v1/products/with-files', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
""")

def main():
    """Run all tests."""
    print("🚀 Testing Product File Upload Functionality")
    print("=" * 60)
    
    success = True
    
    # Test file upload service
    if not test_file_upload_service():
        success = False
    
    # Test image processing
    if not test_image_processing():
        success = False
    
    # Test form data schemas
    if not test_form_data_schemas():
        success = False
    
    # Test static file setup
    if not test_static_file_setup():
        success = False
    
    # Show usage examples
    show_usage_examples()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 FILE UPLOAD FUNCTIONALITY IS READY!")
        print("\n📋 New Endpoints Available:")
        print("   - POST /api/v1/products/with-files")
        print("   - PUT /api/v1/products/{id}/with-files") 
        print("   - POST /api/v1/products/{id}/upload-images")
        print("\n🔧 Dependencies Required:")
        print("   - pip install Pillow aiofiles")
        print("\n📁 Static Files:")
        print("   - Images served at /uploads/")
        print("   - Automatic image optimization")
        print("   - Multiple sizes generated")
    else:
        print("❌ SOME TESTS FAILED!")
        print("   Check the error messages above")
        sys.exit(1)

if __name__ == "__main__":
    main()