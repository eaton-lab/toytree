#!/usr/bin/env python2.7

from __future__ import print_function

from conda_build import api
import re
import os
import sys
import shutil
import shlex
import fileinput
import subprocess



## alternative 
#from gitpython import Repo 


class Version(object):
    def __init__(self, package, initfile, version, releasefile, skip=False):
        
        ## store attrs
        #self.repo = Repo(gitpath)
        self.package = package
        self.init = initfile
        self.nversion = version
        self.release_file = releasefile
        
        ## new args to 
        self.pversion = ""
        self.commits = ""
        if not skip:
            self._get_previous_release_tag()      
            self._get_all_commits_since_last_tag()
        print("Setting new version to {}".format(self.nversion))


    ## command to run all subfunctions
    def push_git_package(self):
        """
        if no conflicts then write new tag to 
        """
        ## check if update is necessary
        if self.nversion == self.pversion:
            raise SystemExit("Exited: new version == existing version")

        ## check for conflicts, then write to local files
        self._pull_from_origin_master()
        self._write_commits_to_release_notes()
        self._write_new_tag_to_init()

        ## push updates; wrapped to ensure we can go back if fails
        try:            
            self._push_new_tag_to_git()
        except:
            self._revert_tag_in_init()



    ## subfunctions ------------------------------------------------
    def _pull_from_origin_master(self):
        """
        Pulls from origin/master, if you have unmerged conflicts
        it will raise an exception. You will need to resolve these.
        """
        try:
            ## self.repo.git.pull()
            subprocess.check_call(["git", "pull"])
        except Exception as inst:
            sys.exit("""
        Your HEAD commit has conflicts with the current origin/master.
        Resolve and merge them then rerun versioner.py
        """)


    def _get_previous_release_tag(self):
        """
        parses init.py to get previous version
        """
        self.pversion = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                        open(self.init, "r").read(),
                        re.M).group(1)
        print("last version - {}".format(self.pversion))



    def _get_all_commits_since_last_tag(self):
        """
        calls git log to complile a change list
        """
        ## check if update is necessary
        if self.nversion == self.pversion:
            raise SystemExit("Exited: new version == existing version")

        cmd = "git log --pretty=oneline {}..".format(self.pversion)
        cmdlist = shlex.split(cmd)
        commits = subprocess.check_output(cmdlist)
        
        ## Split off just the first element, we don't need commit tag
        self.commits = [x.split(" ", 1) for x in commits.split("\n")]



    def _write_commits_to_release_notes(self):
        """
        writes commits to the releasenotes file by appending to the end
        """
        with open(self.release_file, 'a') as out:
            out.write("==========\n{}\n".format(self.nversion))
            for commit in self.commits:
                try:
                    msg = commit[1]
                    if msg != "cosmetic":
                        out.write("-" + msg + "\n")
                except:
                    pass            



    def _write_new_tag_to_init(self):
        """
        Write version to __init__.py by editing in place
        """
        for line in fileinput.input(self.init, inplace=1):
            if line.strip().startswith("__version__"):
                line = "__version__ = \"" + self.nversion + "\""
            print(line.strip("\n"))        



    def _revert_tag_in_init(self):
        """
        Write version to __init__.py by editing in place
        """
        for line in fileinput.input(self.init, inplace=1):
            if line.strip().startswith("__version__"):
                line = "__version__ = \"" + self.pversion + "\""
            print(line.strip("\n"))        



    def _push_new_tag_to_git(self):
        """
        tags a new release and pushes to origin/master
        """
        print("Pushing new version to git")            
        try:
            ## stage the releasefile and initfileb
            #self.repo.git.add(self.release_file)
            #self.repo.git.add(self.init)
            #self.repo.commit...
            subprocess.call(["git", "add", self.release_file])
            subprocess.call(["git", "add", self.init])
            subprocess.call([
                "git", "commit", 
                "-m", "Updating {}/__init__.py to version {}"\
                      .format(self.package, self.nversion)])

            ## push changes to origin master
            subprocess.call(["git", "push", "origin", "master"])

            ## set new tag and push as tagged version
            subprocess.call([
                "git", "tag", 
                "-a", self.nversion,
                "-m", "Updating version to {}".format(self.nversion),
                ])
            subprocess.call(["git", "push", "origin", self.nversion])

        except Exception as e:
            print("Something broke - {}".format(e))
        


    ## builds linux and osx 64-bit versions on py27 and py35
    def build_conda_packages(self):
        """
        Run the Linux build and use converter to build OSX
        """
        ## check if update is necessary
        if self.nversion == self.pversion:
            raise SystemExit("Exited: new version == existing version")

        ## tmp dir
        bldir = "./tmp-bld"
        if not os.path.exists(bldir):
            os.makedirs(bldir)

        ## iterate over builds
        for pybuild in ["2.7", "3"]: #.5", "3.6"]:

            ## build and upload Linux to anaconda.org
            build = api.build(
                "conda-recipe/{}".format(self.package), 
                python=pybuild,
                anaconda_upload=True)

            ## build OSX copies 
            api.convert(build[0], output_dir=bldir, platforms=["osx-64"])

            ## upload OSX copies to anaconda.org
            osxdir = os.path.join(bldir, "osx-64", os.path.basename(build[0]))
            cmd = ["anaconda", "upload", osxdir]
            err = subprocess.Popen(cmd).communicate()

        ## cleanup tmpdir
        shutil.rmtree(bldir)



## MAIN CLI CALL
if __name__ == "__main__":

    ## first check if my forked toyPLOT repo has a new tag
    ## ------- instructions ------------------------------
    ## 1. push new version to toyplot repo
    ## 2. in this repo, uncomment below and fill in new toyplot tag
    toyplot_tag = "0.16.1"
    package = "toyplot"
    init_file = "../toyplot-eaton-lab/toyplot/__init__.py"
    release_file = "../toyplot-eaton-lab/docs/release-notes.rst"
    
    ## Update toyPLOT
    #v = Version(package, init_file, toyplot_tag, release_file, skip=True)
    #v.build_conda_packages()

    ### --------------------------------------------------------
    ## parse command-line args
    new_tag = str(sys.argv[1])
    package = "toytree"
    init_file = "toytree/__init__.py"
    release_file ="./docs/releasenotes.md"

    ## Update toyTREE
    v = Version(package, init_file, new_tag, release_file)
    v.push_git_package()
    v.build_conda_packages()
