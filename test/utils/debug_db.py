import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.db_config import SessionLocal # type: ignore
from services.db_models import UserDB, ProjectDB, SkillDB, UserSkillDB, ProjectInterestDB, ProjectCollaboratorDB # type: ignore

def print_database_state():
    """Prints the current state of test database tables for debugging"""
    db = SessionLocal()
    try:
        # Count rows in each table
        users_count = db.query(UserDB).count()
        projects_count = db.query(ProjectDB).count()
        skills_count = db.query(SkillDB).count()
        user_skills_count = db.query(UserSkillDB).count()
        project_interests_count = db.query(ProjectInterestDB).count()
        project_collabs_count = db.query(ProjectCollaboratorDB).count()
        
        print("\n=== DATABASE STATE ===")
        print(f"Users: {users_count}")
        print(f"Projects: {projects_count}")
        print(f"Skills: {skills_count}")
        print(f"User-Skills: {user_skills_count}")
        print(f"Project Interests: {project_interests_count}")
        print(f"Project Collaborators: {project_collabs_count}")
        
        # List all users
        print("\n--- Users ---")
        for user in db.query(UserDB).all():
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
        
        # List all projects
        print("\n--- Projects ---")
        for project in db.query(ProjectDB).all():
            print(f"ID: {project.id}, Name: {project.project_name}, Creator ID: {project.created_by}")
        
        print("\n=== END DATABASE STATE ===\n")
    finally:
        db.close()

if __name__ == "__main__":
    print_database_state()
