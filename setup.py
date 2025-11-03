from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autosplit",
    version="0.1.0",
    author="Harvey Mondino",
    author_email="your.email@example.com",  # Update this
    description="Split multi-product spreadsheets into individual files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mondinosaur/autosplit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0",
        "openpyxl>=3.0.0",
        "XlsxWriter>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "autosplit=autosplit.cli:main",
        ],
    },
    package_data={
        "autosplit": ["py.typed"],
    },
    zip_safe=False,
)