"""Setup script for Z.AI Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zai-python-sdk",
    version="1.0.0",
    author="Z.AI SDK Team",
    description="Python client library for Z.AI API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zeeeepa/zai-python-sdk",
    packages=find_packages(exclude=["server", "server.*", "tests", "tests.*", "examples", "examples.*"]),
    py_modules=["client", "models"],  # Include root-level modules
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "server": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
            "pydantic>=2.0.0",
        ],
    },
)
