---
section: Getting Started
---


# Contributing

**Collaborator's are very welcome!**

If you haven’t already, you’ll want to first get familiar with the `toytree`
repository at [http://github.com/eaton-lab/toytree](http://github.com/eaton-lab/toytree). 
There you will find the source code and issue tracker where you can inquire
about ongoing development, discuss planned contributions, and volunteer to take
on known issues or future planned developments.

## Organization
As of `toytree` v.3.0 the code base has been reorganized explicitly to better
facilitate collaborative development. This involves the organization of code
into a nested hierarchy of subpackages that share common themes. Many of these
have a clear template structure which can be easily modified or extended to
create new useful methods. For example, a new method could be created for
annotating drawings within the `annotation` subpackage, or a new method for
modifying a tree could be created in the `mod` subpackage. 

## Getting started
To contribute as a developer you'll need to install `toytree` from source
on GitHub and install additional dependencies used for testing the code.
My workflow for this is to clone the repository (in your case, a fork of the
repo) and install in development mode using pip.

```bash
# install dependencies from conda
$ conda install toytree -c eaton-lab --only-deps

# clone the repo and cd into it
$ git clone https://github.com/eaton-lab/toytree.git
$ cd toytree/

# call pip install in 'development mode' (note the '-e .')
$ pip install -e .
```


## Coding Style
The Toyplot source code follows the PEP-8 Style Guide for Python Code.
