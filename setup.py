from setuptools import setup, find_packages

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

VERSION = "2.0.1"
DESCRIPTION = "HTTPInsert - Inserting payloads into all sections of HTTP requests"

setup(
    name="httpinsert",
    version=VERSION,
    author="William Kristoffersen",
    author_email="william.kristof@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["multipart","requests","lxml"],
    keywords=["python", "httpinsert"],
    classifiers=[],
    license="MIT",
)
