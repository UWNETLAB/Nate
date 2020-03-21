from setuptools import setup, find_packages

setup(
    name="nate",
    version="0.0.1",
    install_requires=[
        "pandas>=0.25.0", 
        "spacy", 
        #"python-igraph>=0.8.0", 
        "tok",
        "numba",
        "joblib",
        "matplotlib",
        "networkx",
        "pillow",
        ], # A bunch of things will need to go here; we'll have to do an audit of every package we use
    packages = find_packages(),
    include_package_data=True,
    author = "John McLevey, Tyler Crick, Pierson Browne", # likely more later
    description = "nate (Network Analysis with TExt).",
    url="http://networkslab.org",
	classifiers=(
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	)
)
