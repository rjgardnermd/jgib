from setuptools import setup, find_packages

setup(
    name="jgib",
    packages=find_packages(),  # Automatically finds and includes all submodules in `jgmd`
    version="1.0.0",
    license="MIT",
    description="A general-purpose python package for logging, event-emission, and other common code.",
    author="Jonathan Gardner",
    author_email="jonathangardnermd@outlook.com",
    url="https://github.com/jonathangardnermd/jgmd",
    download_url="https://github.com/jonathangardnermd/jgib/archive/refs/tags/v1.0.0.tar.gz",
    keywords=[
        "PYTHON",
        "LOGGING",
        "EVENTS",
        "UTILITY",
    ],
    install_requires=["tabulate", "python-dotenv", "pydantic"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.13",
    ],
)
