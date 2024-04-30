from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8", errors="ignore") as file:
    requirements = file.read().splitlines()

with open("README.md", "r", encoding="utf-8", errors="ignore") as file:
    readme = file.read()

setup(
    name="stake.py",
    author="yuki",
    version="1.0.0",
    packages=["stake"],
    license="MIT",
    description="Stake(stake.com)用の非公式APIライブラリ",
    long_description=readme,
    install_requires=requirements,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)