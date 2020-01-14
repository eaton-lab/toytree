


<!-- ## update version in __init__ -->
<!-- ... -->

version='0.2.0'

<!-- ## push a tag for version -->
git tag -a $version -m 'tag version $version'
git push --tags 

<!-- ## build 27,35,36,37 for linux and osx -->

<!-- ## build 27,35,36,37 for linux -->
conda-build conda-recipe/toytree/ 

<!-- ## convert for osx and win -->
anaconda upload /home/deren/miniconda3/conda-bld/linux-64/toytree-$version*
conda convert /home/deren/miniconda3/conda-bld/linux-64/toytree-$version* -p osx-64
conda convert /home/deren/miniconda3/conda-bld/linux-64/toytree-$version* -p win-64
anaconda upload osx-64/toytree-$version*
anaconda upload win-64/toytree-$version*

<!--  -->
<!-- ## pip installation -->
python setup.py sdist bdist_wheel
twine upload dist/*

<!--  -->
<!-- ## install test version -->
<!-- twine upload --repository-url https://test.pypi.org/legacy/ dist/* -->
<!--  -->
<!-- ## then test install with: -->
<!-- pip install --index-url https://test.pypi.org/simple/ your-package -->
<!--  -->
<!-- conda install anaconda-client -->
<!-- conda install conda-verify -->