python -m build
twine check dist/*
twine upload -r testpypi dist/*
twine upload dist/*
