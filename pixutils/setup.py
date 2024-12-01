import setuptools

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="pixutils",
    version="1.0",
    author="Sam Lavender, Dean Thomas & Chris Doyle",
    author_email="helpdesk@pixalytics.com",
    description="Pixutils package",
    #long_description=long_description,
    #long_description_content_type="text/markdown",
    #url="https://gitlab.dfms.co.uk/DFMS/Prod-Soil-Moisture",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL-3.0-or-later",
        "Operating System :: OS Independent",
    ),
)