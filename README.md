# repo-structure-generator
repo-structure-generator is a Python tool for generating structured documentation of software repository directory structures. It automatically creates a repo-structure.md file using the tree command output, alongside capturing and including top-of-file comments to provide insights into each directory and file's purpose.

# To Update

```
python setup.py sdist bdist_wheel
twine upload dist/*
```