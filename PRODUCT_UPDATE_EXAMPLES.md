# Product and Image Update - Code Examples

## JavaScript/TypeScript Examples

### 1. Combined Product and Image Update

```javascript
// Using fetch API
async function updateProductWithImages(productId, updateData) {
  const response = await fetch(`/api/v1/products/${productId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`
    },
    body: JSON.stringify({
      // Product details
      name: "Updated Beauty Product",
      description: "New description",
      base_price: 29.99,
      weight: 0.15,
      is_featured: true,
      
      // Images - all in the same request!
      primary_image_url: "https://cdn.example.com/new-primary.jpg",
      thumbnail_url: "https://cdn.example.com/new-thumb.jpg",
      additional_image_urls: [
        "https://cdn.example.com/angle1.jpg",
        "https://cdn.example.com/angle2.jpg",
        "https://cdn.example.com/swatch.jpg"
      ]
    })
  });
  
  if (!response.ok) {
    throw new Error(`Update failed: ${response.statusText}`);
  }
  
  return await response.json();
}

// Usage
try {
  const updatedProduct = await updateProductWithImages(123, updateData);
  console.log('Product updated successfully:', updatedProduct);
} catch (error) {
  console.error('Update failed:', error);
}
```

### 2. Using Axios

```javascript
import axios from 'axios';

const updateProductAndImages = async (productId, updates) => {
  try {
    const response = await axios.put(`/api/v1/products/${productId}`, {
      // Product fields
      name: updates.name,
      base_price: updates.price,
      description: updates.description,
      
      // Image fields
      primary_image_url: updates.primaryImage,
      thumbnail_url: updates.thumbnail,
      additional_image_urls: updates.additionalImages
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Update error:', error.response?.data || error.message);
    throw error;
  }
};
```

### 3. React Hook Example

```typescript
import { useState } from 'react';

interface ProductUpdate {
  name?: string;
  description?: string;
  base_price?: number;
  primary_image_url?: string;
  thumbnail_url?: string;
  additional_image_urls?: string[];
}

const useProductUpdate = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateProduct = async (productId: number, updates: ProductUpdate) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/v1/products/${productId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const updatedProduct = await response.json();
      return updatedProduct;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Update failed';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { updateProduct, loading, error };
};

// Usage in component
const ProductEditForm = ({ productId }: { productId: number }) => {
  const { updateProduct, loading, error } = useProductUpdate();

  const handleSubmit = async (formData: ProductUpdate) => {
    try {
      const updated = await updateProduct(productId, {
        name: formData.name,
        description: formData.description,
        base_price: formData.base_price,
        primary_image_url: formData.primary_image_url,
        additional_image_urls: formData.additional_image_urls
      });
      
      console.log('Product updated:', updated);
    } catch (error) {
      console.error('Failed to update product:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      {loading && <p>Updating...</p>}
      {error && <p>Error: {error}</p>}
    </form>
  );
};
```

## Python Examples

### 1. Using requests library

```python
import requests
import json

def update_product_with_images(product_id, auth_token, updates):
    """Update product and images in a single request."""
    url = f"https://api.example.com/api/v1/products/{product_id}"
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    # Combine product and image updates
    payload = {
        # Product details
        'name': updates.get('name'),
        'description': updates.get('description'),
        'base_price': updates.get('base_price'),
        'weight': updates.get('weight'),
        'is_featured': updates.get('is_featured'),
        
        # Images
        'primary_image_url': updates.get('primary_image_url'),
        'thumbnail_url': updates.get('thumbnail_url'),
        'additional_image_urls': updates.get('additional_image_urls', [])
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Update failed: {e}")
        raise

# Usage
auth_token = "your-jwt-token"
product_id = 123

updates = {
    'name': 'Updated Beauty Product',
    'description': 'New and improved formula',
    'base_price': 29.99,
    'primary_image_url': 'https://cdn.example.com/new-primary.jpg',
    'additional_image_urls': [
        'https://cdn.example.com/angle1.jpg',
        'https://cdn.example.com/angle2.jpg'
    ]
}

try:
    updated_product = update_product_with_images(product_id, auth_token, updates)
    print("Product updated successfully:", updated_product['name'])
except Exception as e:
    print(f"Error: {e}")
```

### 2. Using httpx (async)

```python
import httpx
import asyncio

async def update_product_async(product_id: int, updates: dict, auth_token: str):
    """Async product update with images."""
    url = f"https://api.example.com/api/v1/products/{product_id}"
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.put(url, headers=headers, json=updates)
        response.raise_for_status()
        return response.json()

# Usage
async def main():
    updates = {
        'name': 'Async Updated Product',
        'base_price': 35.99,
        'primary_image_url': 'https://cdn.example.com/async-primary.jpg',
        'additional_image_urls': [
            'https://cdn.example.com/async-1.jpg',
            'https://cdn.example.com/async-2.jpg'
        ]
    }
    
    try:
        result = await update_product_async(123, updates, "your-token")
        print("Async update successful:", result['name'])
    except Exception as e:
        print(f"Async update failed: {e}")

# Run async function
asyncio.run(main())
```

## cURL Examples

### 1. Combined Update

```bash
curl -X PUT "https://api.example.com/api/v1/products/123" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Beauty Product",
    "description": "New description with updated features",
    "base_price": 29.99,
    "weight": 0.15,
    "is_featured": true,
    "primary_image_url": "https://cdn.example.com/new-primary.jpg",
    "thumbnail_url": "https://cdn.example.com/new-thumb.jpg",
    "additional_image_urls": [
      "https://cdn.example.com/angle1.jpg",
      "https://cdn.example.com/angle2.jpg",
      "https://cdn.example.com/swatch.jpg"
    ]
  }'
```

### 2. Partial Update (Name and Primary Image Only)

```bash
curl -X PUT "https://api.example.com/api/v1/products/123" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product Name",
    "primary_image_url": "https://cdn.example.com/updated-image.jpg"
  }'
```

### 3. Image-Only Update

```bash
curl -X PUT "https://api.example.com/api/v1/products/123" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_image_url": "https://cdn.example.com/new-primary.jpg",
    "thumbnail_url": "https://cdn.example.com/new-thumb.jpg",
    "additional_image_urls": [
      "https://cdn.example.com/new-extra1.jpg",
      "https://cdn.example.com/new-extra2.jpg"
    ]
  }'
```

## PHP Examples

### 1. Using cURL

```php
<?php
function updateProductWithImages($productId, $authToken, $updates) {
    $url = "https://api.example.com/api/v1/products/{$productId}";
    
    $headers = [
        'Authorization: Bearer ' . $authToken,
        'Content-Type: application/json'
    ];
    
    $payload = [
        'name' => $updates['name'] ?? null,
        'description' => $updates['description'] ?? null,
        'base_price' => $updates['base_price'] ?? null,
        'primary_image_url' => $updates['primary_image_url'] ?? null,
        'thumbnail_url' => $updates['thumbnail_url'] ?? null,
        'additional_image_urls' => $updates['additional_image_urls'] ?? []
    ];
    
    // Remove null values
    $payload = array_filter($payload, function($value) {
        return $value !== null;
    });
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode >= 200 && $httpCode < 300) {
        return json_decode($response, true);
    } else {
        throw new Exception("Update failed with HTTP code: {$httpCode}");
    }
}

// Usage
$updates = [
    'name' => 'Updated Beauty Product',
    'base_price' => 29.99,
    'primary_image_url' => 'https://cdn.example.com/new-primary.jpg',
    'additional_image_urls' => [
        'https://cdn.example.com/angle1.jpg',
        'https://cdn.example.com/angle2.jpg'
    ]
];

try {
    $result = updateProductWithImages(123, 'your-jwt-token', $updates);
    echo "Product updated: " . $result['name'] . "\n";
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

## Key Points

1. **Single Endpoint**: Use `PUT /api/v1/products/{product_id}` for all updates
2. **Partial Updates**: Only include fields you want to change
3. **Image Arrays**: `additional_image_urls` accepts an array of URLs
4. **Authentication**: Always include the Bearer token
5. **Content-Type**: Use `application/json`
6. **Error Handling**: Check HTTP status codes and handle errors appropriately

## Response Format

All successful updates return the complete product object:

```json
{
  "id": 123,
  "name": "Updated Product Name",
  "description": "Updated description",
  "base_price": 29.99,
  "sku": "PROD-123",
  "primary_image_url": "https://cdn.example.com/primary.jpg",
  "thumbnail_url": "https://cdn.example.com/thumb.jpg",
  "all_image_urls": [
    "https://cdn.example.com/primary.jpg",
    "https://cdn.example.com/angle1.jpg",
    "https://cdn.example.com/angle2.jpg"
  ],
  "display_image_url": "https://cdn.example.com/primary.jpg",
  "is_active": true,
  "is_featured": false,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T11:00:00Z",
  "owner_id": 456
}
```