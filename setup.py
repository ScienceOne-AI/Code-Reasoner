from setuptools import setup, find_packages

setup(
    name="s1-evole",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-generativeai",
        "volcengine-python-sdk[ark]",
        "pyyaml",
        "pillow",
        "numpy",
        "loguru",
        "tqdm",
    ],
    python_requires=">=3.8",
) 