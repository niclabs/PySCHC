""" setup file """

import setuptools

with open("../../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="schc-fragmentation",
    version="0.0.1",
    author="Juan Saez Hidalgo",
    author_email="juan.saez.hidalgo@gmail.com",
    description="Fragmentation Layer of SCHC protocols",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
)
