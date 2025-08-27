from setuptools import setup, find_packages

setup(
    name='ENVT',
    version='0.0.1',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "envt = envt.main:main"
        ]
    },
    install_requires=[],
    python_requires='>=3.9',
)