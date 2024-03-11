
# 1. increase version, commit tag, push
git tag -a 3.0.0 -m "tag version 3.0.0"
git push origin 3.0.0

# 2. pip upload version from source
python setup.py sdist bdist_wheel
twine upload --repository testpypi dist/*
twine upload --repository pypi dist/*

# 3. conda-forge upload from tagged version
# clone my fork of the conda-forge toytre-feedstock
git clone ...
# edit recipe/meta.yaml to update version
cd ...
git add recipe/meta.yaml 
git commit -m "new release "
# push and check that it passed auto checks
git push origin main
