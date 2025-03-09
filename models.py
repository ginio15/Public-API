"""
Models module for the GrapeVine application.
Defines Pydantic models for data validation, serialization, and API documentation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List , Any         
from enum import Enum

class SkillLevel(str, Enum):
    """Enum representing different programming skill proficiency levels."""
    beginner = "beginner"      
    experienced = "experienced" 
    expert = "expert"          

class ProgrammingLanguage(str, Enum):
    """Enum representing supported programming languages in the application."""
    cpp = "C++"                
    javascript = "Javascript"  
    python = "Python"          
    java = "Java"              
    lua = "Lua"                
    rust = "Rust"              
    go = "Go"                  
    julia = "Julia"            

class Skill(BaseModel):
    """Model representing a user's programming skill."""
    language: ProgrammingLanguage 
    level: SkillLevel             

class UserBase(BaseModel):
    """Base model with common user attributes."""
    first_name: str           
    last_name: str            
    email: EmailStr           
    age: int = Field(..., ge=13, description="User must be at least 13")
    country: str              
    residence: str            
    username: str             

class UserCreate(UserBase):
    """Model for creating a new user, extends UserBase with password."""
    password: str             

class User(UserBase):
    """Complete user model including database fields and related properties."""
    user_id: int              # Unique identifier for the user in the database
    skills: List[Skill] = []  # List of programming skills, limited to 3 per user

class ProjectBase(BaseModel):
    """Base model with common project attributes."""
    project_name: str = Field(..., min_length=1)  # Project name, must not be empty
    description: Optional[str] = None            # Optional project description
    maximum_collaborators: int = Field(..., gt=0)  # Maximum number of collaborators allowed
    
    @validator('project_name')
    def project_name_must_not_be_whitespace_only(cls, v):
        """Validate that project name is not just whitespace."""
        if v.strip() == "":
            raise ValueError("Project name cannot be whitespace only")
        return v

class ProjectCreate(ProjectBase):
    """Model for creating a new project."""
    pass  # Inherits all fields from ProjectBase without modification

class Project(ProjectBase):
    """Complete project model including database fields and relationships."""
    project_id: int                # Unique identifier for the project
    collaborators: List[User] = [] # List of users collaborating on the project
    created_by: str                # Username of the project creator
    is_completed: bool = False     # Flag indicating whether the project is completed

class AddSkillRequest(BaseModel):
    """Request model for adding a skill to a user."""
    username: str  # Username of the user to add the skill to
    skill: Skill   # The skill to add

class RemoveSkillRequest(BaseModel):
    """Request model for removing a skill from a user."""
    username: str                # Username of the user to remove the skill from
    language: ProgrammingLanguage  # The programming language skill to remove
