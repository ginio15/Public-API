from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from .db_config import Base 

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    country = Column(String, nullable=False)
    residence = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)   # In a real system, store a HASH
    
    # Relationships
    skills = relationship("UserSkillDB", back_populates="user", cascade="all, delete-orphan")
    projects_created = relationship("ProjectDB", back_populates="creator", foreign_keys="ProjectDB.created_by")
    project_interests = relationship("ProjectInterestDB", back_populates="user", cascade="all, delete-orphan")
    project_collaborations = relationship("ProjectCollaboratorDB", back_populates="user", cascade="all, delete-orphan")

class SkillDB(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(String, nullable=False)  # e.g. "Python"
    level = Column(String, nullable=False)     # e.g. "expert"

class UserSkillDB(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"))

    # relationships
    user = relationship("UserDB", back_populates="skills")
    skill = relationship("SkillDB")

class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    maximum_collaborators = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    is_completed = Column(Boolean, default=False)

    # Relationships
    creator = relationship("UserDB", back_populates="projects_created", foreign_keys=[created_by])
    interests = relationship("ProjectInterestDB", back_populates="project", cascade="all, delete-orphan")
    collaborators = relationship("ProjectCollaboratorDB", back_populates="project", cascade="all, delete-orphan")

class ProjectInterestDB(Base):
    __tablename__ = "project_interests"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    project = relationship("ProjectDB", back_populates="interests")
    user = relationship("UserDB", back_populates="project_interests")

class ProjectCollaboratorDB(Base):
    __tablename__ = "project_collaborators"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    project = relationship("ProjectDB", back_populates="collaborators")
    user = relationship("UserDB", back_populates="project_collaborations")

