"""
Setup script for Multi-Agent Translation Pipeline & Turing Machine Simulator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="translation-tm-simulator",
    version="1.0.0",
    author="M.Sc. Project Team",
    author_email="your.email@example.com",
    description="Multi-agent translation pipeline and Turing machine simulator for studying semantic drift",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ex3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.1.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "sentence-transformers>=2.2.0",
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "pandas>=2.0.0",
        "scipy>=1.10.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "pylint>=2.17.0",
            "mypy>=1.4.0",
        ],
        "notebook": [
            "jupyter>=1.0.0",
            "notebook>=7.0.0",
            "seaborn>=0.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "my_tool=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.json", "*.yaml"],
    },
)
