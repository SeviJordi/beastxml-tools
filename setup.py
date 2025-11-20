from setuptools import setup, find_packages

setup(
    name="beastxml-tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "lxml",
        "rich",
        "typer"
    ],
    entry_points={
        "console_scripts": [
            "beastxml = beastxml_tools.cli:app"
        ]
    },
    python_requires=">=3.9",
)