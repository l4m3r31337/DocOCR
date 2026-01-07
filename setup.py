from setuptools import setup, find_packages

setup(
    name="doc-processor",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},  # Указываем где искать пакеты
    install_requires=[
        'pytesseract>=0.3.10',
        'pdf2image>=1.17.0',
        'Pillow>=10.1.0',
        'PyPDF2>=3.0.1',
    ],
    entry_points={
        'console_scripts': [
            'doc-processor=cli:main',  # Теперь cli в src
        ],
    },
)