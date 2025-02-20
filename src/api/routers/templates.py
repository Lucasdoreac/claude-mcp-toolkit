"""
Template endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.database import get_db
from src.api.auth.router import get_current_user
from src.api.models.database_models import User
from src.api.models.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateRead,
    TemplateInstanceCreate,
    TemplateInstanceRead
)
from src.api.services.template_service import TemplateService

router = APIRouter(prefix="/api/templates", tags=["templates"])

@router.post("", response_model=TemplateRead)
async def create_template(
    template: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new template."""
    try:
        template_service = TemplateService(db)
        return template_service.create_template(template, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[TemplateRead])
async def get_templates(
    type: Optional[str] = Query(None, description="Filter by template type"),
    active_only: bool = Query(True, description="Only return active templates"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all templates."""
    template_service = TemplateService(db)
    return template_service.get_templates(type, active_only)

@router.get("/{template_id}", response_model=TemplateRead)
async def get_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific template."""
    template_service = TemplateService(db)
    template = template_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/{template_id}", response_model=TemplateRead)
async def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a template."""
    try:
        template_service = TemplateService(db)
        template = template_service.update_template(
            template_id,
            template_update,
            current_user.id
        )
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a template."""
    template_service = TemplateService(db)
    try:
        if template_service.delete_template(template_id):
            return {"message": "Template deleted"}
        raise HTTPException(status_code=404, detail="Template not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/type/{type}/default", response_model=TemplateRead)
async def get_default_template(
    type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get default template for a type."""
    template_service = TemplateService(db)
    template = template_service.get_default_template(type)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"No default template found for type {type}"
        )
    return template

@router.post("/instance", response_model=TemplateInstanceRead)
async def create_instance(
    instance: TemplateInstanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a template instance."""
    try:
        template_service = TemplateService(db)
        return template_service.create_instance(
            instance.template_id,
            instance.variables,
            current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{template_id}/render")
async def render_template(
    template_id: int,
    variables: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Render a template without creating an instance."""
    try:
        template_service = TemplateService(db)
        template = template_service.get_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
            
        content = template_service.render_template(template, variables)
        return {"content": content}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))