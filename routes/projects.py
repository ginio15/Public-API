from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import ProjectCreate, Project, User, Skill
from services.db.db_config import SessionLocal
from services.db.db_models import ProjectDB, UserDB, ProjectInterestDB, ProjectCollaboratorDB

router = APIRouter()

def get_db():
    # Dependency that provides a SQLAlchemy session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/create-project", response_model=Project)
def create_project(project_data: ProjectCreate, creator_username: str, db: Session = Depends(get_db)):
    # Check if the creator exists
    creator = db.query(UserDB).filter(UserDB.username == creator_username).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Create a new project
    new_project = ProjectDB(
        project_name=project_data.project_name,
        description=project_data.description,
        maximum_collaborators=project_data.maximum_collaborators,
        created_by=creator.id,
        is_completed=False
    )
    
    # Add the new project to the database
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Return the new project as a Project model instance
    return Project(
        project_id=new_project.id,
        project_name=new_project.project_name,
        description=new_project.description,
        maximum_collaborators=new_project.maximum_collaborators,
        collaborators=[],
        created_by=creator_username,
        is_completed=False
    )

@router.delete("/delete-project")
def delete_project(project_id: int, requesting_username: str, db: Session = Depends(get_db)):
    # Check if the project exists
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    # Check if the requesting user exists
    user = db.query(UserDB).filter(UserDB.username == requesting_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Check if the requestor is the creator of the project
    if project.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator of the project can delete it."
        )

    # Delete the project
    db.delete(project)
    db.commit()

    # Return a success message
    return {"message": f"Project with id {project_id} deleted successfully."}

@router.post("/complete-project")
def complete_project(project_id: int, requesting_username: str, db: Session = Depends(get_db)):
    # Check if the project exists
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    # Check if the requesting user exists
    user = db.query(UserDB).filter(UserDB.username == requesting_username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Only the creator can complete the project
    if project.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator of the project can complete it."
        )

    # Mark as completed
    project.is_completed = True
    db.commit()

    return {"message": f"Project {project_id} is now marked as completed."}

# Only showing the express_interest_in_project function with the added check


@router.post("/express-interest")
def express_interest_in_project(project_id: int, username: str, db: Session = Depends(get_db)):
    # Check if project exists
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    # Check if user exists
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    #  Check if user is creator 
    if project.created_by == user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project creator cannot express interest in their own project."
        )

    # Check if project is completed
    if project.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot express interest in a completed project."
        )

    # Check if user is already a collaborator
    existing_collab = db.query(ProjectCollaboratorDB).filter(
        ProjectCollaboratorDB.project_id == project_id,
        ProjectCollaboratorDB.user_id == user.id
    ).first()
    if existing_collab:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a collaborator on this project."
        )

    # Check if user has already expressed interest
    existing_interest = db.query(ProjectInterestDB).filter(
        ProjectInterestDB.project_id == project_id,
        ProjectInterestDB.user_id == user.id
    ).first()
    if existing_interest:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has already expressed interest."
        )

    # Add user to interest_requests
    new_interest = ProjectInterestDB(project_id=project_id, user_id=user.id)
    db.add(new_interest)
    db.commit()
    
    return {"message": f"User {username} expressed interest in project {project_id}."}


@router.post("/respond-interest")
def respond_interest(
    project_id: int,
    requesting_username: str,
    interested_username: str,
    decision: str,  # "accept" or "decline"
    db: Session = Depends(get_db)
):
    # Check if project exists
    project = db.query(ProjectDB).filter(ProjectDB.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found."
        )

    # Check if requestor is the project creator
    requestor = db.query(UserDB).filter(UserDB.username == requesting_username).first()
    if not requestor or project.created_by != requestor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creator of the project can respond to interests."
        )

    # Check if the project is completed
    if project.is_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot accept or decline after project is completed."
        )

    # Get the interested user
    interested_user = db.query(UserDB).filter(UserDB.username == interested_username).first()
    if not interested_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Check if the interested_username is in interest_requests
    interest_record = db.query(ProjectInterestDB).filter(
        ProjectInterestDB.project_id == project_id,
        ProjectInterestDB.user_id == interested_user.id
    ).first()
    
    if not interest_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User did not express interest or already processed."
        )

    # Process the decision
    if decision.lower() == "decline":
        # Remove them from interest_requests
        db.delete(interest_record)
        db.commit()
        return {
            "message": f"User {interested_username} has been declined for project {project_id}."
        }
    elif decision.lower() == "accept":
        # Check if we have space in collaborators
        collab_count = db.query(ProjectCollaboratorDB).filter(
            ProjectCollaboratorDB.project_id == project_id
        ).count()
        
        if collab_count >= project.maximum_collaborators:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project is already at maximum collaborator capacity."
            )
            
        # Add as collaborator
        new_collab = ProjectCollaboratorDB(
            project_id=project_id,
            user_id=interested_user.id
        )
        db.add(new_collab)
        
        # Remove from interest_requests
        db.delete(interest_record)
        db.commit()
        
        return {
            "message": f"User {interested_username} accepted to project {project_id}.",
            "collaborators_count": collab_count + 1
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be either 'accept' or 'decline'."
        )

@router.get("/open-seats")
def list_projects_with_open_seats(db: Session = Depends(get_db)):
    # Query for all non-completed projects
    projects = db.query(ProjectDB).filter(ProjectDB.is_completed == False).all()
    
    open_projects = []
    for project in projects:
        # Count collaborators
        collab_count = db.query(ProjectCollaboratorDB).filter(
            ProjectCollaboratorDB.project_id == project.id
        ).count()
        
        # Check if there are open seats
        if collab_count < project.maximum_collaborators:
            # Get creator info
            creator = db.query(UserDB).filter(UserDB.id == project.created_by).first()
            
            # Get current collaborators
            collaborators = []
            for collab in db.query(ProjectCollaboratorDB).filter(
                ProjectCollaboratorDB.project_id == project.id
            ).all():
                user = db.query(UserDB).filter(UserDB.id == collab.user_id).first()
                if user:
                    # For simplicity, just include username in this example
                    collaborators.append({"username": user.username})
            
            # Get interest requests 
            interest_requests = []
            for interest in db.query(ProjectInterestDB).filter(
                ProjectInterestDB.project_id == project.id
            ).all():
                user = db.query(UserDB).filter(UserDB.id == interest.user_id).first()
                if user:
                    interest_requests.append(user.username)
            
            open_projects.append({
                "project_id": project.id,
                "project_name": project.project_name,
                "description": project.description,
                "maximum_collaborators": project.maximum_collaborators,
                "collaborators": collaborators,
                "created_by": creator.username if creator else "Unknown",
                "interest_requests": interest_requests
            })
    
    return open_projects
