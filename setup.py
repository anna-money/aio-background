import re
from pathlib import Path

from setuptools import setup

install_requires = ["croniter>=1.0.1"]


def read(*parts):
    return Path(__file__).resolve().parent.joinpath(*parts).read_text().strip()


def read_version():
    regexp = re.compile(r"^__version__\W*=\W*\"([\d.abrc]+)\"")
    for line in read("aio_background", "__init__.py").splitlines():
        match = regexp.match(line)
        if match is not None:
            return match.group(1)
    else:
        raise RuntimeError("Cannot find version in aio_background/__init__.py")


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="aio-background",
    version=read_version(),
    description="A thing to run tasks in the background",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=["macOS", "POSIX", "Windows"],
    author="Yury Pliner",
    python_requires=">=3.9",
    project_urls={},
    author_email="yury.pliner@gmail.com",
    license="MIT",
    packages=["aio_background"],
    package_dir={"aio_background": "./aio_background"},
    package_data={"aio_background": ["py.typed"]},
    install_requires=install_requires,
    include_package_data=True,
)
