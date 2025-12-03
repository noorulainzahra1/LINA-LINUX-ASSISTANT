#!/usr/bin/env python3
"""
LINA Setup Script - Simple Python Package Installation
======================================================

Standard setuptools-based setup script for LINA (Linux Intelligence Network Assistant).

Usage:
    python setup.py install     # Install LINA
    python setup.py develop     # Install in development mode

Author: LINA Development Team
Version: 3.0.0
License: MIT
"""

import sys
from setuptools import setup, find_packages

# Ensure Python version compatibility
if sys.version_info < (3, 8):
    print("Error: LINA requires Python 3.8 or higher")
    sys.exit(1)

# Core requirements - only the essential packages
requirements = [
    "python-dotenv>=1.0.0",
    "rich>=13.7.0",
    "google-generativeai>=0.3.2",
    "requests>=2.31.0",
    "psutil>=5.9.6",
    "typing-extensions>=4.8.0",
    "pydantic>=2.5.0",
    "cryptography>=41.0.7",
    "urllib3>=2.1.0",
]

setup(
    name="lina-ai",
    version="3.0.0",
    description="AI-Powered Cybersecurity Platform with Phoenix Architecture",
    author="LINA Development Team",
    author_email="lina@example.com",
    url="https://github.com/your-username/lina-ai",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "lina=main:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],
    license="MIT",
    zip_safe=False,
)
