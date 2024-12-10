from setuptools import setup, find_packages

setup(
    name="jgib",
    packages=find_packages(),  # Automatically finds and includes all submodules in `jgmd`
    version="7.0.0",
    license="MIT",
    description="A general-purpose python package for logging, event-emission, and other common code.",
    author="Jonathan Gardner",
    author_email="rjgardnermd@gardnermoneygrowth.com",
    url="https://github.com/rjgardnermd/jgib",
    download_url="https://github.com/rjgardnermd/jgib/archive/refs/tags/v7.0.0.tar.gz",
    keywords=[
        "PYTHON",
        "IBKR",
        "DTO",
        "MODELS",
    ],
    install_requires=["pydantic", "websockets", "jgmd"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.13",
    ],
)
