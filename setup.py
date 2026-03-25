from setuptools import find_packages, setup


setup(
    name="mmw-agent",
    version="0.1.0",
    description="Math Modeling workflow agents built on ConnectOnion",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={"mmw_agent": ["config/*.toml"]},
    python_requires=">=3.10",
    install_requires=[
        "connectonion>=0.8.6",
        "jupyter-client>=8.6.0",
        "nbformat>=5.10.0",
        "ansi2html>=1.9.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "requests>=2.31.0",
        "tomli>=2.0.1; python_version < '3.11'",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "mmw-agent=mmw_agent.cli:main",
        ]
    },
)
