# GrapeVine Project

GrapeVine is a collaboration platform designed to help developers find and join programming projects. It enables users to showcase their skills, create projects, and find collaborators with complementary skill sets.

## Features

- **User Management**: Register accounts, update profiles, and showcase programming skills
- **Project Creation**: Create projects and specify required collaborators
- **Skill Matching**: Find projects that match your skill set
- **Collaboration System**: Express interest in projects and manage collaborators

## Technology Stack

- **Backend**: FastAPI, Python 3.12
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Authentication**: JWT token-based auth
- **Testing**: Pytest with 30+ test cases

## Getting Started

### Prerequisites

- Python 3.8+ (3.12 recommended)
- pip (Python package manager)
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ginio15/grapevine.git
   cd grapevine
   ```

2. Create a virtual environment:
   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python -m services.init_db
   ```

5. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

6. The API will be available at [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Alternative API Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Authentication
- `POST /auth/login` - Login and get access token

### Users
- `POST /users/register` - Register a new user
- `POST /users/reset-password` - Reset password
- `POST /users/add-skill` - Add a programming skill
- `DELETE /users/remove-skill` - Remove a skill
- `GET /users/stats` - Get user statistics
- `GET /users/me` - Get own user profile

### Projects
- `POST /projects/create-project` - Create a new project
- `DELETE /projects/delete-project` - Delete a project
- `POST /projects/complete-project` - Mark project as completed
- `POST /projects/express-interest` - Express interest in a project
- `POST /projects/respond-interest` - Accept or decline interest requests
- `GET /projects/open-seats` - List projects with open seats

## Running Tests

Run the test suite to ensure everything is working:

```bash
pytest
```

For more detailed test output:

```bash                      
pytest -v
```

## Project Structure

```
GrapeVine/
├── main.py                   # FastAPI application entry point
├── models.py                 # Pydantic models for request/response validation
├── requirements.txt          # Project dependencies
├── setup.py                  # Setup script for easy installation
├── .gitignore                # Files to exclude from version control
├── README.md                 # Project documentation
│
├── routes/                   # API route definitions
│   ├── auth.py               # Authentication endpoints
│   ├── projects.py           # Project management endpoints
│   └── users.py              # User management endpoints
│
├── services/                 # Core backend services
│   ├──auth/
│   │  ├── auth_config.py     # Authentication configuration
│   │  └── security.py        # Password hashing and security functions
│   │
│   └──db/
│       ├── db_config.py      # Database configuration
│       ├── db_models.py      # SQLAlchemy ORM models
│       └── init_db.py        # Database initialization script
│      
│
└── test/                     # Test suite
    ├── test_auth.py          # Authentication tests
    ├── test_main.py          # Main application tests
    ├── test_projects.py      # Project endpoint tests
    ├── test_users.py         # User endpoint tests
    ├── test_validation.py    # Input validation tests
    ├── conftest.py           # Configure Pytest
    └── utils/                    
        ├── debug_db.py       # Database debugging utility
        └── clear_skills.py   # Utility to clear skills
```

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
