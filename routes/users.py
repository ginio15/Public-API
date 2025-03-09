from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy import func
from services.auth.security import hash_password, verify_password 
from models import UserCreate, User, AddSkillRequest, RemoveSkillRequest, Skill
from services.db.db_config import SessionLocal
from services.db.db_models import UserDB, SkillDB, UserSkillDB, ProjectDB, ProjectCollaboratorDB

router = APIRouter()

def get_db():
    # Dependency that provides a SQLAlchemy session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=User)
def register_user(user_create: UserCreate, db: Session = Depends(get_db)):

    # Check if username already exists
    existing_user = db.query(UserDB).filter(UserDB.username == user_create.username).first()
    # Check if email already exists
    existing_email = db.query(UserDB).filter(UserDB.email == user_create.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken."
        )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use."
        )

    hashed_pw = hash_password(user_create.password)

    new_user = UserDB(
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        email=user_create.email,
        age=user_create.age,
        country=user_create.country,
        residence=user_create.residence,
        username=user_create.username,
        password=hashed_pw,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return User(
        user_id=new_user.id,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        email=new_user.email,
        age=new_user.age,
        country=new_user.country,
        residence=new_user.residence,
        username=new_user.username,
        skills=[]
    )



@router.post("/reset-password")
def reset_password(username: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    hashed_pw = hash_password(new_password)
    user.password = hashed_pw
    db.commit()

    return {"message": f"Password for {username} has been updated."}


@router.post("/add-skill")
def add_skill(req: AddSkillRequest, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(UserDB).filter(UserDB.username == req.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # 2. Check if user already has 3 skills
    user_skill_count = db.query(UserSkillDB).filter(UserSkillDB.user_id == user.id).count()
    if user_skill_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has 3 skills. Remove one before adding a new one."
        )

    # 3. Check if this skill already exists for the user
    existing_skills = db.query(UserSkillDB).join(SkillDB).filter(
        UserSkillDB.user_id == user.id,
        SkillDB.language == req.skill.language
    ).first()
    
    if existing_skills:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill with this language already exists."
        )

    # 4. Find or create the skill
    skill = db.query(SkillDB).filter(
        SkillDB.language == req.skill.language,
        SkillDB.level == req.skill.level
    ).first()
    
    if not skill:
        skill = SkillDB(
            language=req.skill.language,
            level=req.skill.level
        )
        db.add(skill)
        db.flush()  # Generate ID without committing transaction

    # 5. Add the new user skill link
    user_skill = UserSkillDB(
        user_id=user.id,
        skill_id=skill.id
    )
    db.add(user_skill)
    db.commit()

    # 6. Get updated skills for response
    user_skills = []
    for user_skill in db.query(UserSkillDB).join(SkillDB).filter(UserSkillDB.user_id == user.id).all():
        skill_obj = db.query(SkillDB).filter(SkillDB.id == user_skill.skill_id).first()
        user_skills.append({
            "language": skill_obj.language,
            "level": skill_obj.level
        })

    return {
        "message": "Skill added successfully",
        "skills": user_skills
    }

@router.delete("/remove-skill")
def remove_skill(req: RemoveSkillRequest, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(UserDB).filter(UserDB.username == req.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # 2. Find the skill to remove
    user_skill = db.query(UserSkillDB).join(SkillDB).filter(
        UserSkillDB.user_id == user.id,
        SkillDB.language == req.language
    ).first()

    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User does not have skill in {req.language}."
        )

    # 3. Remove the skill
    db.delete(user_skill)
    db.commit()

    # 4. Get updated skills for response
    user_skills = []
    for user_skill in db.query(UserSkillDB).join(SkillDB).filter(UserSkillDB.user_id == user.id).all():
        skill_obj = db.query(SkillDB).filter(SkillDB.id == user_skill.skill_id).first()
        user_skills.append({
            "language": skill_obj.language,
            "level": skill_obj.level
        })

    return {
        "message": f"Removed {req.language} skill from user {req.username}",
        "skills": user_skills
    }

@router.get("/stats")
def get_user_stats(username: str, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(UserDB).filter(UserDB.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # 2. Count projects created by this user
    projects_created = db.query(ProjectDB).filter(ProjectDB.created_by == user.id).count()

    # 3. Count projects where the user is a collaborator
    projects_contributed = db.query(ProjectCollaboratorDB).filter(
        ProjectCollaboratorDB.user_id == user.id
    ).count()

    return {
        "username": username,
        "projects_created": projects_created,
        "projects_contributed": projects_contributed
    }

from .auth import get_current_user

@router.get("/me")
def read_own_profile(current_user: UserDB = Depends(get_current_user)):
    # The user is guaranteed to be valid here
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "age": current_user.age,
        "country": current_user.country,
        "residence": current_user.residence
    }