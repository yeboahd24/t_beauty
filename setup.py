"""
Setup script for T-Beauty Business Management System.
"""
from setuptools import setup, find_packages

setup(
    name="tbeauty",
    version="1.0.0",
    description="T-Beauty Business Management System",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "email-validator>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "httpx>=0.24.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ]
    }
)