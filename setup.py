from setuptools import setup, find_packages

setup(
    name="hypergraphify",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "stim>=1.10",
        "numpy>=1.20",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pymatching>=2.0",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Transform quantum LDPC codes for MWPM decoding",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/HyperGraphify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.8",
)
