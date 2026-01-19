from setuptools import setup, find_packages

setup(
    name="doc-processor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip() for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        'console_scripts': [
            'doc-processor=src.cli:main',
        ],
    },
    python_requires='>=3.11',
)