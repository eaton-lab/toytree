# make sure we're in the top dir
cd /home/deren/Documents/toytree/docs

# remove last build
rm -r _build

# convert notebooks to rsts
jupyter-nbconvert --to rst sandbox/tutorial.ipynb --output-dir rsts
jupyter-nbconvert --to rst sandbox/node_labels.ipynb --output-dir rsts
jupyter-nbconvert --to rst sandbox/tip_labels.ipynb --output-dir rsts
jupyter-nbconvert --to rst sandbox/cloud-trees.ipynb --output-dir rsts

# build docs which links to docs/rsts from docs/index.rst
make html

# return to whereever we started
cd -
