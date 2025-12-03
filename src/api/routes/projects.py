"""
Project routes.
"""
from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, Depends

from src.api.schemas.projects import ProjectCreate, ProjectUpdate, ProjectResponse
from src.api.dependencies import get_db_session
from src.database.repositories import ProjectRepository

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_db_session),
):
    """List all projects."""
    repo = ProjectRepository(session)
    projects = await repo.get_all(skip=skip, limit=limit)
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    session=Depends(get_db_session),
):
    """Get a project by ID."""
    repo = ProjectRepository(session)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/district/{district}", response_model=List[ProjectResponse])
async def get_projects_by_district(
    district: str,
    session=Depends(get_db_session),
):
    """Get projects by district."""
    repo = ProjectRepository(session)
    projects = await repo.get_by_district(district)
    return projects


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    session=Depends(get_db_session),
):
    """Create a new project."""
    repo = ProjectRepository(session)
    project = await repo.create(
        name=data.name,
        description=data.description,
        district=data.district,
        address=data.address,
        reference=data.reference,
        details=data.details,
        video_url=data.video_url,
        brochure_url=data.brochure_url,
        includes_parking=data.includes_parking,
        has_showroom=data.has_showroom,
    )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    data: ProjectUpdate,
    session=Depends(get_db_session),
):
    """Update a project."""
    repo = ProjectRepository(session)
    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated = await repo.update(
        project,
        name=data.name,
        description=data.description,
        district=data.district,
        address=data.address,
        reference=data.reference,
        details=data.details,
        video_url=data.video_url,
        brochure_url=data.brochure_url,
        includes_parking=data.includes_parking,
        has_showroom=data.has_showroom,
    )
    return updated


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    session=Depends(get_db_session),
):
    """Delete a project."""
    repo = ProjectRepository(session)
    deleted = await repo.delete_by_id(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")

