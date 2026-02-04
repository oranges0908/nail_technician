import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.service import (
    ServiceRecordCreate,
    ServiceRecordUpdate,
    ServiceRecordComplete,
    ServiceRecordResponse,
    ComparisonResultResponse
)
from app.services.service_record_service import ServiceRecordService
from app.services.analysis_service import AnalysisService
from app.core.dependencies import get_current_active_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ServiceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_service_record(
    service: ServiceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建服务记录

    - **customer_id**: 客户ID（必填）
    - **design_plan_id**: 设计方案ID（可选）
    - **service_date**: 服务日期
    - **service_duration**: 服务时长（分钟，可选）
    - **materials_used**: 材料清单（可选）
    - **artist_review**: 美甲师复盘（可选）
    - **customer_feedback**: 客户反馈（可选）
    - **customer_satisfaction**: 客户满意度 1-5 星（可选）
    """
    try:
        service_record = ServiceRecordService.create_service(
            db=db,
            service_data=service.model_dump(),
            user_id=current_user.id
        )
        return service_record
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{service_id}", response_model=ServiceRecordResponse)
async def get_service_record(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取服务记录详情
    """
    service = ServiceRecordService.get_service_by_id(
        db=db,
        service_id=service_id,
        user_id=current_user.id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"服务记录 {service_id} 不存在"
        )

    return service


@router.get("/", response_model=List[ServiceRecordResponse])
async def list_service_records(
    customer_id: Optional[int] = Query(None, description="按客户ID过滤"),
    status_filter: Optional[str] = Query(None, alias="status", description="按状态过滤（pending/completed）"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数上限"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    列出服务记录

    - 支持按客户ID过滤
    - 支持按状态过滤
    - 支持分页
    """
    services = ServiceRecordService.list_services(
        db=db,
        user_id=current_user.id,
        customer_id=customer_id,
        status=status_filter,
        skip=skip,
        limit=limit
    )

    return services


@router.put("/{service_id}", response_model=ServiceRecordResponse)
async def update_service_record(
    service_id: int,
    update_data: ServiceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新服务记录
    """
    try:
        service = ServiceRecordService.update_service(
            db=db,
            service_id=service_id,
            update_data=update_data.model_dump(exclude_unset=True),
            user_id=current_user.id
        )
        return service
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{service_id}/complete", response_model=ServiceRecordResponse)
async def complete_service_record(
    service_id: int,
    completion_data: ServiceRecordComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    完成服务记录并触发 AI 综合分析

    **必填字段**：
    - **actual_image_path**: 实际完成图路径
    - **service_duration**: 实际服务时长（分钟）

    **可选字段**：
    - **materials_used**: 实际使用的材料清单
    - **artist_review**: 美甲师复盘内容
    - **customer_feedback**: 客户反馈
    - **customer_satisfaction**: 客户满意度评分（1-5星）
    - **notes**: 其他备注

    完成后会自动触发 AI 综合分析，分析结果可通过 GET /{service_id}/comparison 查看
    """
    try:
        # 1. 更新服务记录
        service = ServiceRecordService.complete_service(
            db=db,
            service_id=service_id,
            completion_data=completion_data.model_dump(),
            user_id=current_user.id
        )

        # 2. 自动触发 AI 综合分析（后台异步执行）
        try:
            await AnalysisService.analyze_service(db=db, service_record_id=service_id)
            logger.info(f"服务记录 {service_id} 的 AI 分析已完成")
        except Exception as e:
            # 分析失败不影响服务记录保存，只记录日志
            logger.error(f"服务记录 {service_id} 的 AI 分析失败: {e}")
            # 不抛出异常，让服务记录仍然成功保存

        return service

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_record(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除服务记录

    会级联删除关联的对比结果和能力记录
    """
    try:
        ServiceRecordService.delete_service(
            db=db,
            service_id=service_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{service_id}/comparison", response_model=ComparisonResultResponse)
async def get_comparison_result(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取服务记录的 AI 对比分析结果

    如果尚未分析，可以手动触发分析
    """
    # 验证服务记录存在且属于当前用户
    service = ServiceRecordService.get_service_by_id(
        db=db,
        service_id=service_id,
        user_id=current_user.id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"服务记录 {service_id} 不存在"
        )

    # 获取对比结果
    comparison = service.comparison_result

    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"服务记录 {service_id} 尚未进行 AI 分析，请先完成服务记录或手动触发分析"
        )

    return comparison


@router.post("/{service_id}/analyze", response_model=ComparisonResultResponse)
async def trigger_analysis(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    手动触发 AI 综合分析

    用于：
    - 服务记录已完成但未分析的情况
    - 更新了复盘或反馈内容后重新分析
    """
    # 验证服务记录存在且属于当前用户
    service = ServiceRecordService.get_service_by_id(
        db=db,
        service_id=service_id,
        user_id=current_user.id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"服务记录 {service_id} 不存在"
        )

    try:
        comparison = await AnalysisService.analyze_service(
            db=db,
            service_record_id=service_id
        )
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
