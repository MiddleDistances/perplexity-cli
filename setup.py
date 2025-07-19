"""
Setup configuration for perplexity-cli
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="perplexity-cli",
    version="1.0.0",
    author="Michael Freiberg",
    author_email="your.email@example.com",  # Update this
    description="A command-line interface for Perplexity AI with improved error handling and API key management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dawid-szewc/perplexity-cli",
    packages=find_packages(),
    py_modules=["perplexity_improved"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "perplexity=perplexity_improved:main",
        ],
    },
    keywords="perplexity ai cli api chatbot",
    project_urls={
        "Bug Reports": "https://github.com/dawid-szewc/perplexity-cli/issues",
        "Source": "https://github.com/dawid-szewc/perplexity-cli",
    },
)