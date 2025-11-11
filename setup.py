from setuptools import setup, find_packages

setup(
    name="zos_mips_prediction",
    version="0.1.0",
    description="Machine Learning system for z/OS MIPS consumption prediction",
    author="Perf_Plan Team",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "joblib>=1.0.0",
        "tqdm>=4.62.0",
        "pyyaml>=5.4.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
