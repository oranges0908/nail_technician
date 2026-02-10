"""
文件上传 API 测试 (P1)
覆盖: /api/v1/uploads — 文件上传成功、类型校验、扩展名拒绝
"""
import io
import os
import tempfile
from unittest.mock import patch

from app.api.v1.uploads import UPLOAD_BASE_DIR


class TestUploadFile:
    """文件上传"""

    def test_upload_nail_photo_success(self, client, auth_headers, tmp_path):
        """上传指甲照片成功返回 201"""
        # 使用临时目录作为上传目录
        with patch("app.api.v1.uploads.UPLOAD_BASE_DIR", tmp_path):
            file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
            response = client.post(
                "/api/v1/uploads/nails",
                files={
                    "file": ("test_nail.png", io.BytesIO(file_content), "image/png")
                },
                headers=auth_headers,
            )
            assert response.status_code == 201
            data = response.json()
            assert data["content_type"] == "image/png"
            assert "file_url" in data
            assert data["file_size"] > 0

    def test_upload_inspiration_image(self, client, auth_headers, tmp_path):
        """上传灵感图成功"""
        with patch("app.api.v1.uploads.UPLOAD_BASE_DIR", tmp_path):
            file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # JPEG header
            response = client.post(
                "/api/v1/uploads/inspirations",
                files={
                    "file": ("ref.jpg", io.BytesIO(file_content), "image/jpeg")
                },
                headers=auth_headers,
            )
            assert response.status_code == 201

    def test_reject_invalid_extension(self, client, auth_headers):
        """拒绝不支持的文件扩展名"""
        file_content = b"not an image"
        response = client.post(
            "/api/v1/uploads/nails",
            files={
                "file": ("test.txt", io.BytesIO(file_content), "image/png")
            },
            headers=auth_headers,
        )
        assert response.status_code == 400

    def test_reject_invalid_content_type(self, client, auth_headers):
        """拒绝不支持的 Content-Type"""
        file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        response = client.post(
            "/api/v1/uploads/nails",
            files={
                "file": ("test.png", io.BytesIO(file_content), "text/plain")
            },
            headers=auth_headers,
        )
        assert response.status_code == 400


class TestDeleteUploadedFile:
    """删除上传文件"""

    def test_delete_nonexistent_file(self, client, auth_headers):
        """删除不存在的文件返回 404"""
        response = client.delete(
            "/api/v1/uploads/nails/nonexistent.jpg",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_delete_invalid_category(self, client, auth_headers):
        """无效分类返回 400"""
        response = client.delete(
            "/api/v1/uploads/invalid_category/test.jpg",
            headers=auth_headers,
        )
        assert response.status_code == 400
