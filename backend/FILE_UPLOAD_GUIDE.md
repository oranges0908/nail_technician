# File Upload API Guide

## Overview

The file upload system supports uploading and managing 4 types of nail art images:

1. **Customer Nail Photos** (`/uploads/nails`) - Customer's nail characteristics
2. **Inspiration Images** (`/uploads/inspirations`) - Reference images for design generation
3. **Design Images** (`/uploads/designs`) - AI-generated or manually uploaded design plans
4. **Actual Result Photos** (`/uploads/actuals`) - Completed service photos

## Features

✅ **File Validation**
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`
- Max file size: 10MB
- Content-Type validation

✅ **Unique Filename Generation**
- Format: `{timestamp}_{uuid}_{original_name}.ext`
- Prevents filename collisions
- Preserves original filename for reference

✅ **Chunked Upload**
- 8KB chunk size for memory efficiency
- Supports large files up to 10MB
- Automatic cleanup on failure

✅ **Batch Upload**
- Upload up to 10 files at once
- Partial success handling (some files succeed, some fail)
- Detailed error reporting per file

✅ **Static File Serving**
- Uploaded files accessible at `/uploads/{category}/{filename}`
- Proper Content-Type headers
- Direct browser access supported

## API Endpoints

### 1. Upload Customer Nail Photo

```http
POST /api/v1/uploads/nails
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: <binary data>
```

**Response (201 Created):**
```json
{
  "filename": "20260203_233032_d5adf4bb_test_nail.png",
  "file_path": "uploads/nails/20260203_233032_d5adf4bb_test_nail.png",
  "file_url": "/uploads/nails/20260203_233032_d5adf4bb_test_nail.png",
  "file_size": 2790,
  "content_type": "image/png",
  "uploaded_at": "2026-02-03T23:30:32.461835"
}
```

**Usage Example (Python):**
```python
import requests

files = {'file': open('nail_photo.jpg', 'rb')}
headers = {'Authorization': 'Bearer YOUR_TOKEN'}

response = requests.post(
    'http://localhost:8000/api/v1/uploads/nails',
    files=files,
    headers=headers
)

data = response.json()
print(f"File uploaded: {data['file_url']}")
```

**Usage Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/v1/uploads/nails" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@nail_photo.jpg"
```

### 2. Upload Inspiration Image

```http
POST /api/v1/uploads/inspirations
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: <binary data>
```

### 3. Upload Design Image

```http
POST /api/v1/uploads/designs
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: <binary data>
```

### 4. Upload Actual Result Photo

```http
POST /api/v1/uploads/actuals
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: <binary data>
```

### 5. Batch Upload

Upload multiple files at once (max 10 files).

```http
POST /api/v1/uploads/batch/{category}
Content-Type: multipart/form-data
Authorization: Bearer {token}

files: <binary data>
files: <binary data>
files: <binary data>
```

**Categories:**
- `nails`
- `inspirations`
- `designs`
- `actuals`

**Response (201 Created):**
```json
{
  "uploaded_files": [
    {
      "filename": "20260203_233032_3e83aec2_inspiration1.png",
      "file_path": "uploads/inspirations/20260203_233032_3e83aec2_inspiration1.png",
      "file_url": "/uploads/inspirations/20260203_233032_3e83aec2_inspiration1.png",
      "file_size": 2790,
      "content_type": "image/png",
      "uploaded_at": "2026-02-03T23:30:32.461835"
    },
    ...
  ],
  "failed_files": [
    {
      "filename": "invalid.txt",
      "error": "不支持的文件格式 .txt"
    }
  ],
  "total_count": 3,
  "success_count": 2,
  "failed_count": 1
}
```

**Usage Example (Python):**
```python
files = [
    ('files', open('image1.jpg', 'rb')),
    ('files', open('image2.png', 'rb')),
    ('files', open('image3.jpg', 'rb'))
]

response = requests.post(
    'http://localhost:8000/api/v1/uploads/batch/inspirations',
    files=files,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

data = response.json()
print(f"Uploaded: {data['success_count']}/{data['total_count']}")
```

### 6. Delete Uploaded File

```http
DELETE /api/v1/uploads/{category}/{filename}
Authorization: Bearer {token}
```

**Example:**
```http
DELETE /api/v1/uploads/nails/20260203_233032_d5adf4bb_test_nail.png
```

**Response (204 No Content):**
```
(Empty body)
```

**Note:** This only deletes the physical file. Database records must be cleaned up separately by business logic.

## Access Uploaded Files

Uploaded files are served as static files:

```
http://localhost:8000/uploads/{category}/{filename}
```

**Example:**
```
http://localhost:8000/uploads/nails/20260203_233032_d5adf4bb_test_nail.png
http://localhost:8000/uploads/designs/20260203_233032_b20b10b3_design_purple.png
```

These URLs can be:
- Embedded in HTML `<img>` tags
- Used in CSS `background-image`
- Accessed directly in browser
- Used as input for AI analysis APIs

## Error Handling

### 400 Bad Request

**Unsupported File Format:**
```json
{
  "detail": "不支持的文件格式 .txt，仅支持: .webp, .jpeg, .png, .jpg"
}
```

**Invalid Category:**
```json
{
  "detail": "不支持的分类 'invalid'，仅支持: nails, inspirations, designs, actuals"
}
```

**Too Many Files in Batch:**
```json
{
  "detail": "批量上传最多支持10个文件"
}
```

### 401 Unauthorized

```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found

```json
{
  "detail": "文件不存在: test.png"
}
```

### 413 Payload Too Large

```json
{
  "detail": "文件过大，最大允许 10.0MB"
}
```

### 500 Internal Server Error

```json
{
  "detail": "文件保存失败: Permission denied"
}
```

## Integration with Business Logic

### Creating a Service Record with Uploaded Images

```python
# 1. Upload design image
design_response = requests.post(
    'http://localhost:8000/api/v1/uploads/designs',
    files={'file': open('design.png', 'rb')},
    headers={'Authorization': f'Bearer {token}'}
)
design_url = design_response.json()['file_path']

# 2. Upload actual result image
actual_response = requests.post(
    'http://localhost:8000/api/v1/uploads/actuals',
    files={'file': open('actual.jpg', 'rb')},
    headers={'Authorization': f'Bearer {token}'}
)
actual_url = actual_response.json()['file_path']

# 3. Complete service record (triggers AI analysis)
service_data = {
    "actual_image_path": actual_url,
    "service_duration": 120,
    "artist_review": "颜色搭配很好，时间有点紧张",
    "customer_feedback": "非常满意，颜色很漂亮",
    "customer_satisfaction": 5
}

service_response = requests.put(
    f'http://localhost:8000/api/v1/services/{service_id}/complete',
    json=service_data,
    headers={'Authorization': f'Bearer {token}'}
)
```

### Generating Design with Inspiration Images

```python
# 1. Upload multiple inspiration images
files = [
    ('files', open('inspo1.jpg', 'rb')),
    ('files', open('inspo2.png', 'rb'))
]

batch_response = requests.post(
    'http://localhost:8000/api/v1/uploads/batch/inspirations',
    files=files,
    headers={'Authorization': f'Bearer {token}'}
)

inspiration_urls = [
    file['file_path'] for file in batch_response.json()['uploaded_files']
]

# 2. Generate design using AI (to be implemented)
design_data = {
    "customer_profile_id": 1,
    "inspiration_images": inspiration_urls,
    "design_prompt": "粉色渐变 + 珍珠装饰"
}

# POST /api/v1/designs/generate
```

## File Storage Structure

```
backend/
└── uploads/
    ├── nails/
    │   └── 20260203_233032_d5adf4bb_test_nail.png
    ├── inspirations/
    │   ├── 20260203_233032_3e83aec2_inspiration1.png
    │   └── 20260203_233032_dc5f7566_inspiration_ocean.png
    ├── designs/
    │   └── 20260203_233032_b20b10b3_design_purple.png
    └── actuals/
        └── 20260203_233032_235b449b_actual_result.png
```

## Security Considerations

✅ **Path Traversal Protection**
- Filenames are validated and sanitized
- Delete endpoint checks file path is within allowed directory
- No directory listing exposed

✅ **File Type Validation**
- Extension whitelist: `.jpg`, `.jpeg`, `.png`, `.webp`
- Content-Type validation
- Rejects executable files

✅ **Size Limits**
- 10MB per file
- Chunked reading prevents memory exhaustion
- Automatic cleanup on oversized files

✅ **Authentication Required**
- All upload endpoints require valid JWT token
- User ID associated with uploads (for future audit trail)

⚠️ **Future Enhancements**
- Add virus scanning (ClamAV integration)
- Add image format validation (verify actual content, not just extension)
- Add watermarking for designs
- Implement user storage quotas
- Add CDN integration for production

## Testing

Run the comprehensive test suite:

```bash
cd backend
python test_upload_api.py
```

**Test Coverage:**
- ✅ Upload customer nail photo
- ✅ Upload inspiration image
- ✅ Upload design image
- ✅ Upload actual result photo
- ✅ Batch upload (3 files)
- ✅ Invalid file type rejection
- ✅ Large file rejection
- ✅ Static file access

## Configuration

Edit `backend/.env`:

```bash
# Maximum file size (bytes)
MAX_UPLOAD_SIZE=10485760  # 10MB

# Upload directory (relative to backend/)
UPLOAD_DIR=uploads
```

## Production Deployment Checklist

- [ ] Enable virus scanning
- [ ] Configure CDN for static files (CloudFront, Cloudflare)
- [ ] Set up S3/MinIO for file storage
- [ ] Enable image optimization (auto-resize, compression)
- [ ] Configure backup for upload directory
- [ ] Set up log rotation for upload logs
- [ ] Implement user storage quotas
- [ ] Add image watermarking for copyright protection
- [ ] Configure CORS for production frontend domain
- [ ] Set up monitoring for upload failures

## Troubleshooting

**Problem: 401 Unauthorized**
- Ensure JWT token is included in Authorization header
- Verify token hasn't expired
- Check user account is active

**Problem: File not found after upload**
- Check `uploads/` directory permissions (must be writable)
- Verify `UPLOAD_DIR` in `.env` is correct
- Check disk space availability

**Problem: Static file 404**
- Ensure FastAPI static file mounting is configured in `main.py`
- Verify file URL matches actual file path
- Check file wasn't deleted manually

**Problem: Slow upload for large files**
- Check network bandwidth
- Consider increasing chunk size (currently 8KB)
- Enable gzip compression on reverse proxy (nginx)

## Support

For issues or questions:
- Check API documentation: http://localhost:8000/docs
- Review test script: `backend/test_upload_api.py`
- Check server logs: `backend/logs/` (if configured)
