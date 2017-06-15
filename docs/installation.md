

# Installation
You can install toytree and its dependencies ([toyplot](http://toyplot.readthedocs.io) and [numpy](http://numpy.readthedocs.io/en/latest/user/index.html)) with a single command using the software package manager [conda](https://conda.io/docs/install/quick.html). 
Toytree is currently hosted on the 'eaton-lab' channel on anaconda, which must be specified with the -c flag. 

```bash
conda install toytree -c eaton-lab
```

<p></p>
### Specify versions
Toytree is new and under active development so you may wish 
to select a specific version during installation to ensure that 
changes to toytree do not break compatibility with your
scripts. You can specify version with conda.  
```bash
conda install toytree=0.1.2 -c eaton-lab
```  

<p></p>
### Alternative installation
You can alternatively install toytree from github along with its dependencies using pip with the following commands:

```bash
## install toyplot numpy and toyplot
pip install numpy
pip install toyplot
git clone https://github.com/eaton-lab/toytree.git
cd toytree/
pip install .
```