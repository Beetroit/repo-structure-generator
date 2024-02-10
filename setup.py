from setuptools import setup, find_packages

setup(
    name="repo-structure-generator",
    version="1.2.0",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here if you have any
    ],
    entry_points={
        "console_scripts": [
            "repo-structure-generator = repo_structure_generator.generator:main",
        ],
    },
    # Metadata
    author="Marco Acea",
    author_email="aceamarco@gmail.com",
    description="A tool for generating structured documentation of software repository directory structures.",
    url="https://github.com/aceamarco/repo-structure-generator",
    license="MIT",
)
