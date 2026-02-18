"""
文件上传 API

支持上传4种类型的图片：
1. 客户指甲照片 (/uploads/nails)
2. 灵感参考图 (/uploads/inspirations)
3. AI生成设计图 (/uploads/designs)
4. 实际完成图 (/uploads/actuals)
"""
import io
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


# 配置
UPLOAD_BASE_DIR = Path(settings.UPLOAD_DIR)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}
ALLOWED_PIL_FORMATS = {"JPEG", "PNG", "WEBP"}

# 上传子目录
UPLOAD_CATEGORIES = {
    "nails": "nails",           # 客户指甲照片
    "inspirations": "inspirations",  # 灵感参考图
    "designs": "designs",       # AI生成设计图
    "actuals": "actuals"        # 实际完成图
}


class UploadResponse(BaseModel):
    """文件上传响应"""
    filename: str
    file_path: str
    file_url: str
    file_size: int
    content_type: str
    uploaded_at: str


class BatchUploadResponse(BaseModel):
    """批量上传响应"""
    uploaded_files: List[UploadResponse]
    failed_files: List[dict]
    total_count: int
    success_count: int
    failed_count: int


def validate_file(file: UploadFile) -> None:
    """
    验证上传文件

    Args:
        file: 上传的文件

    Raises:
        HTTPException: 文件验证失败
    """
    # 检查文件是否存在
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供文件"
        )

    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式 {file_ext}，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 检查 Content-Type（仅接受标准图片 MIME 类型）
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型 {file.content_type}，仅支持: image/jpeg, image/png, image/webp"
        )


async def _validate_image_magic(file: UploadFile) -> None:
    """
    用 PIL 读取文件头，验证实际内容为合法图片。
    防止攻击者通过伪造扩展名或 Content-Type 头上传非图片文件。
    """
    header = await file.read(4096)
    await file.seek(0)
    try:
        img = Image.open(io.BytesIO(header))
        if img.format not in ALLOWED_PIL_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"图片格式不支持: {img.format}，仅支持 JPEG/PNG/WEBP"
            )
    except HTTPException:
        raise
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的图片文件，无法识别图片内容"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片文件验证失败"
        )


def generate_unique_filename(original_filename: str) -> str:
    """
    生成唯一文件名（避免冲突）

    格式: {timestamp}_{uuid}_{original_name}

    Args:
        original_filename: 原始文件名

    Returns:
        str: 唯一文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    file_ext = Path(original_filename).suffix.lower()
    safe_name = Path(original_filename).stem[:50]  # 限制文件名长度

    return f"{timestamp}_{unique_id}_{safe_name}{file_ext}"


async def save_upload_file(
    file: UploadFile,
    category: str,
    user_id: int
) -> UploadResponse:
    """
    保存上传文件

    Args:
        file: 上传的文件
        category: 文件分类（nails/inspirations/designs/actuals）
        user_id: 用户ID

    Returns:
        UploadResponse: 上传响应

    Raises:
        HTTPException: 保存失败
    """
    # 验证文件（扩展名 + Content-Type 头）
    validate_file(file)

    # 验证文件真实内容（魔数校验，防止 Content-Type 伪造）
    await _validate_image_magic(file)

    # 生成唯一文件名
    unique_filename = generate_unique_filename(file.filename)

    # 构建保存路径
    category_dir = UPLOAD_BASE_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    file_path = category_dir / unique_filename

    # 保存文件（分块写入以支持大文件）
    try:
        file_size = 0
        with open(file_path, "wb") as f:
            while chunk := await file.read(8192):  # 8KB chunks
                file_size += len(chunk)

                # 检查文件大小
                if file_size > MAX_FILE_SIZE:
                    f.close()
                    file_path.unlink()  # 删除已写入的部分文件
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"文件过大，最大允许 {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                    )

                f.write(chunk)

        logger.info(f"文件上传成功: {file_path} ({file_size} bytes)")

        # 构建文件 URL（相对于静态文件挂载点）
        relative_path = f"{category}/{unique_filename}"
        file_url = f"/uploads/{relative_path}"

        return UploadResponse(
            filename=unique_filename,
            file_path=str(file_path),
            file_url=file_url,
            file_size=file_size,
            content_type=file.content_type,
            uploaded_at=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件保存失败: {e}")
        # 清理已创建的文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )


@router.post("/nails", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_nail_photo(
    file: UploadFile = File(..., description="客户指甲照片"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传客户指甲照片

    用于创建客户档案时记录客户的指甲特征
    """
    return await save_upload_file(file, "nails", current_user.id)


@router.post("/inspirations", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_inspiration_image(
    file: UploadFile = File(..., description="灵感参考图"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传灵感参考图

    用于AI设计生成的参考素材
    """
    return await save_upload_file(file, "inspirations", current_user.id)


@router.post("/designs", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_design_image(
    file: UploadFile = File(..., description="设计方案图"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传设计方案图

    用于保存AI生成或手动上传的设计图
    """
    return await save_upload_file(file, "designs", current_user.id)


@router.post("/actuals", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_actual_photo(
    file: UploadFile = File(..., description="实际完成图"),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传实际完成图

    用于完成服务记录时记录实际效果
    """
    return await save_upload_file(file, "actuals", current_user.id)


@router.post("/batch/{category}", response_model=BatchUploadResponse, status_code=status.HTTP_201_CREATED)
async def batch_upload_files(
    category: str,
    files: List[UploadFile] = File(..., description="批量上传的文件"),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量上传文件

    Args:
        category: 文件分类（nails/inspirations/designs/actuals）
        files: 文件列表（最多10个）

    Returns:
        BatchUploadResponse: 批量上传结果
    """
    # 验证分类
    if category not in UPLOAD_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的分类 '{category}'，仅支持: {', '.join(UPLOAD_CATEGORIES.keys())}"
        )

    # 限制批量上传数量
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="批量上传最多支持10个文件"
        )

    uploaded_files = []
    failed_files = []

    for file in files:
        try:
            result = await save_upload_file(file, category, current_user.id)
            uploaded_files.append(result)
        except HTTPException as e:
            failed_files.append({
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })

    return BatchUploadResponse(
        uploaded_files=uploaded_files,
        failed_files=failed_files,
        total_count=len(files),
        success_count=len(uploaded_files),
        failed_count=len(failed_files)
    )


@router.delete("/{category}/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_uploaded_file(
    category: str,
    filename: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除上传的文件

    Args:
        category: 文件分类
        filename: 文件名

    注意：仅删除文件，不删除数据库记录（需要业务层处理）
    """
    # 验证分类
    if category not in UPLOAD_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的分类 '{category}'"
        )

    # 构建文件路径
    file_path = UPLOAD_BASE_DIR / category / filename

    # 检查文件是否存在
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {filename}"
        )

    # 安全检查：确保文件路径在允许的目录内（防止路径穿越攻击）
    try:
        file_path.resolve().relative_to(UPLOAD_BASE_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="非法的文件路径"
        )

    # 删除文件
    try:
        file_path.unlink()
        logger.info(f"文件删除成功: {file_path}")
    except Exception as e:
        logger.error(f"文件删除失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )
