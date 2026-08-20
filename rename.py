import os
import glob

files = glob.glob('src/**/*.py', recursive=True) + ['pyproject.toml', 'test_run.py']
for f in files:
    if os.path.isfile(f):
        with open(f, 'r', encoding='utf-8') as file:
            c = file.read()
        c = c.replace('unidoc', 'doctensor')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(c)

os.rename('src/unidoc', 'src/doctensor')
