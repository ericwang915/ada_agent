from setuptools import setup, find_packages

setup(
    name="ada_agent",
    version="0.1.0",
    description="ADA: Python LLM Agent with Customizable Skills, Memory, Knowledge RAG & Persona",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/ericwang915/ada_agent",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "openai",
        "python-dotenv",
        "duckduckgo-search",
    ],
    extras_require={
        "all": ["anthropic", "google-generativeai"],
        "anthropic": ["anthropic"],
        "gemini": ["google-generativeai"],
    },
    entry_points={
        "console_scripts": [
            "ada=ada_agent.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
