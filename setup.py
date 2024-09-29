import setuptools
import os
import re


def get_version():
    init_path = os.path.join(
        os.path.dirname(__file__), "pdf_namer", "__init__.py"
    )
    with open(init_path, "r", encoding="utf-8") as f:
        content = f.read()
    version_match = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in __init__.py")


def get_requirements():
    requirements_path = os.path.join(
        os.path.dirname(__file__), "requirements.txt"
    )
    with open(requirements_path, "r", encoding="utf-8") as f:
        return [
            line.strip() for line in f
            if line.strip() and not line.startswith("#")
        ]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pdf-namer",
    version=get_version(),
    author="Laurence Labusch",
    author_email="laurence.labusch@gmail.com",
    description="A Linux-specific tool for naming PDF files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/llabusch93/pdf-namer",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'pdf-namer=pdf_namer.main:main',
        ],
    },
)