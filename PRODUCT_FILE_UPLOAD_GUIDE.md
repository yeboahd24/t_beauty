# Product File Upload Guide

## ✅ NEW: File Upload Functionality Implemented!

I've implemented comprehensive file upload functionality for product images. Now you can upload actual image files instead of providing URLs.

## 🚀 New Endpoints

### 1. Create Product with Files
**POST** `/api/v1/products/with-files`
- Content-Type: `multipart/form-data`
- Upload product data + images in a single request

### 2. Update Product with Files  
**PUT** `/api/v1/products/{product_id}/with-files`
- Content-Type: `multipart/form-data`
- Update product data + upload new images

### 3. Upload Images Only
**POST** `/api/v1/products/{product_id}/upload-images`
- Content-Type: `multipart/form-data`
- Upload images for existing product

## 📋 Form Fields

### Product Data Fields:
- `name` (required): Product name
- `description`: Product description
- `base_price` (required): Product price
- `sku` (required): Stock keeping unit
- `brand_id`: Brand ID
- `category_id`: Category ID
- `weight`: Product weight
- `dimensions`: Product dimensions
- `is_active`: Active status (default: true)
- `is_featured`: Featured status (default: false)
- `is_discontinued`: Discontinued status (default: false)

### Image Upload Fields:
- `primary_image`: Main product image file
- `thumbnail_image`: Thumbnail image file (optional - auto-generated)
- `additional_images`: Array of additional image files

## 🖼️ Image Processing Features

### Automatic Image Processing:
1. **Validation**: File type, size, format validation
2. **Variants**: Automatically creates multiple sizes:
   - **Original**: Full-size uploaded image
   - **Medium**: Resized to max 800x800px (for display)
   - **Thumbnail**: Resized to 200x200px (for lists)
3. **Optimization**: JPEG compression for web delivery
4. **Organization**: Files organized by user and product ID

### Supported Formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### File Size Limits:
- Maximum file size: 10MB per image
- Automatic compression and optimization

## 📝 Usage Examples

### 1. Create Product with Images (cURL)

```bash
curl -X POST "http://localhost:8000/api/v1/products/with-files" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "name=Beauty Product with Images" \
  -F "description=A beautiful product with uploaded images" \
  -F "base_price=29.99" \
  -F "sku=BEAUTY-001" \
  -F "weight=0.15" \
  -F "is_featured=true" \
  -F "primary_image=@/path/to/primary-image.jpg" \
  -F "additional_images=@/path/to/angle1.jpg" \
  -F "additional_images=@/path/to/angle2.jpg"
```

### 2. Update Product with New Images (cURL)

```bash
curl -X PUT "http://localhost:8000/api/v1/products/5/with-files" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "name=Updated Product Name" \
  -F "base_price=35.99" \
  -F "primary_image=@/path/to/new-primary.jpg" \
  -F "additional_images=@/path/to/new-extra.jpg"
```

### 3. Upload Images Only (cURL)

```bash
curl -X POST "http://localhost:8000/api/v1/products/5/upload-images" \
  -H "Authorization: Bearer your-jwt-token" \
  -F "primary_image=@/path/to/primary.jpg" \
  -F "additional_images=@/path/to/extra1.jpg" \
  -F "additional_images=@/path/to/extra2.jpg" \
  -F "replace_existing=false"
```

## 🌐 JavaScript/Frontend Examples

### 1. Using FormData with Fetch

```javascript
async function createProductWithImages(productData, imageFiles) {
  const formData = new FormData();
  
  // Add product data
  formData.append('name', productData.name);
  formData.append('description', productData.description);
  formData.append('base_price', productData.base_price);
  formData.append('sku', productData.sku);
  formData.append('is_featured', productData.is_featured);
  
  // Add image files
  if (imageFiles.primary) {
    formData.append('primary_image', imageFiles.primary);
  }
  
  if (imageFiles.additional) {
    imageFiles.additional.forEach(file => {
      formData.append('additional_images', file);
    });
  }
  
  const response = await fetch('/api/v1/products/with-files', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`
    },
    body: formData
  });
  
  return await response.json();
}

// Usage
const productData = {
  name: 'Beauty Product',
  description: 'A great product',
  base_price: 29.99,
  sku: 'BEAUTY-001',
  is_featured: true
};

const imageFiles = {
  primary: primaryImageFile, // File object from input
  additional: [extraImage1, extraImage2] // Array of File objects
};

try {
  const result = await createProductWithImages(productData, imageFiles);
  console.log('Product created:', result);
} catch (error) {
  console.error('Error:', error);
}
```

### 2. React Component Example

```jsx
import React, { useState } from 'react';

const ProductUploadForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    base_price: '',
    sku: '',
    is_featured: false
  });
  
  const [images, setImages] = useState({
    primary: null,
    additional: []
  });
  
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setUploading(true);
    
    const uploadData = new FormData();
    
    // Add form fields
    Object.keys(formData).forEach(key => {
      uploadData.append(key, formData[key]);
    });
    
    // Add images
    if (images.primary) {
      uploadData.append('primary_image', images.primary);
    }
    
    images.additional.forEach(file => {
      uploadData.append('additional_images', file);
    });
    
    try {
      const response = await fetch('/api/v1/products/with-files', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: uploadData
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Product created:', result);
        // Reset form or redirect
      } else {
        console.error('Upload failed');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} encType="multipart/form-data">
      <input
        type="text"
        placeholder="Product Name"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        required
      />
      
      <input
        type="number"
        step="0.01"
        placeholder="Price"
        value={formData.base_price}
        onChange={(e) => setFormData({...formData, base_price: e.target.value})}
        required
      />
      
      <input
        type="text"
        placeholder="SKU"
        value={formData.sku}
        onChange={(e) => setFormData({...formData, sku: e.target.value})}
        required
      />
      
      <label>
        Primary Image:
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImages({...images, primary: e.target.files[0]})}
        />
      </label>
      
      <label>
        Additional Images:
        <input
          type="file"
          accept="image/*"
          multiple
          onChange={(e) => setImages({...images, additional: Array.from(e.target.files)})}
        />
      </label>
      
      <button type="submit" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Create Product'}
      </button>
    </form>
  );
};

export default ProductUploadForm;
```

## 📁 File Storage Structure

```
uploads/
└── images/
    └── products/
        └── {user_id}/
            └── {product_id}/
                ├── primary_uuid.jpg          # Original primary image
                ├── medium_primary_uuid.jpg   # Medium-sized primary
                ├── thumb_primary_uuid.jpg    # Thumbnail primary
                ├── additional_1_uuid.jpg     # Original additional
                ├── medium_additional_1_uuid.jpg
                ├── thumb_additional_1_uuid.jpg
                └── ...
```

## 🔗 Generated URLs

The API automatically generates URLs for different image sizes:

```json
{
  "id": 123,
  "name": "Beauty Product",
  "primary_image_url": "/uploads/images/products/1/123/medium_primary_abc123.jpg",
  "thumbnail_url": "/uploads/images/products/1/123/thumb_primary_abc123.jpg",
  "all_image_urls": [
    "/uploads/images/products/1/123/medium_primary_abc123.jpg",
    "/uploads/images/products/1/123/medium_additional_1_def456.jpg",
    "/uploads/images/products/1/123/medium_additional_2_ghi789.jpg"
  ],
  "display_image_url": "/uploads/images/products/1/123/medium_primary_abc123.jpg"
}
```

## ⚙️ Configuration

### Dependencies Added:
- `Pillow==10.1.0` - Image processing
- `aiofiles==23.2.1` - Async file operations

### Static File Serving:
- Uploaded images served at `/uploads/` path
- Automatic directory creation
- Secure file access (user-specific directories)

## 🔒 Security Features

1. **File Type Validation**: Only allowed image formats
2. **Size Limits**: Maximum 10MB per file
3. **User Isolation**: Files organized by user ID
4. **Unique Filenames**: UUID-based naming prevents conflicts
5. **Path Sanitization**: Secure file path handling

## 🚀 Benefits

1. **No External Dependencies**: Self-hosted file storage
2. **Automatic Optimization**: Multiple image sizes generated
3. **Form Data Support**: Standard HTML form uploads
4. **Async Processing**: Non-blocking file operations
5. **Error Handling**: Graceful failure handling
6. **Backward Compatible**: Original URL-based endpoints still work

## 🧪 Testing

You can test the file upload functionality using:
1. **Postman**: Create multipart/form-data requests
2. **cURL**: Use the examples above
3. **Frontend Forms**: HTML file input elements
4. **API Documentation**: Visit `/docs` for interactive testing

The file upload system is now ready for production use! 🎉