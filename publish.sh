#!/bin/bash
#!/bin/bash
pip install --upgrade build

# generar dist
python setup.py sdist bdist_wheel

twine upload dist/*
