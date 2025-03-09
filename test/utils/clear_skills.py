import sys
import os

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy.orm import Session
from services.db_config import SessionLocal, engine, Base # type: ignore
from services.db_models import UserDB, SkillDB, UserSkillDB # type: ignore

def clear_all_skills():
    """Utility function to clear all skills from the database"""
    db = SessionLocal()
    try:
        print("Clearing all user skills...")
        user_skills_count = db.query(UserSkillDB).delete()
        print(f"Deleted {user_skills_count} user-skill associations")
        
        skills_count = db.query(SkillDB).delete()
        print(f"Deleted {skills_count} skills")
        
        db.commit()
        print("Done!")
    except Exception as e:
        db.rollback()
        print(f"Error clearing skills: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_all_skills()
