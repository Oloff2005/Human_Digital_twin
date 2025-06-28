from setuptools import setup, find_packages

setup(
    name='human-digital-twin',
    version='0.1.0',
    description='A modular simulation engine for modeling human physiology using digital twin principles.',
    author='Your Name',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'pydantic',
        'matplotlib',
        'streamlit',
        'fastapi',
        'uvicorn',
        'scipy',
        'pyyaml',
        'seaborn==0.13.2',
        'pandas'
    ],
    entry_points={
        'console_scripts': [
            'hdt=hdt.cli:main',
            'run_hdt=hdt.cli:main',
        ],
    },
)