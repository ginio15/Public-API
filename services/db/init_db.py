from .db_config import engine, Base
from .db_models import UserDB, ProjectDB, SkillDB, UserSkillDB, ProjectInterestDB, ProjectCollaboratorDB

def initialize_database():
    """
    Initialize the database by creating all tables defined in the models.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    initialize_database()
