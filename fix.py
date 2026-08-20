with open('pyproject.toml', 'a') as f:
    f.write('\n[tool.setuptools.packages.find]\nwhere = ["src"]\n')
