#!/usr/bin/env python2.7

from __future__ import print_function

from conda_build import api
import re
import os
import sys
import shutil
import shlex
import argparse
import fileinput
import subprocess

#import git


class Version(object):
    def __init__(self, package, branch, tag, deploy):
        
        ## store attrs
        self.package = package
        self.branch = branch
        self.tag = tag
        self.deploy = deploy
        self.commits = []
        self.init_version = ""

        ## filepaths
        self.release_file = os.path.join("./", "docs", "releasenotes.md")
        self.init_file = os.path.join("./", self.package, "__init__.py") 
        self.meta_yaml = os.path.join("./conda-recipe", self.package, "meta.yaml")

        ## can only deploy from master
        if self.deploy and not self.branch == "master":
            sys.exit("Error: can only deploy from master branch")


    def get_git_status(self):
        """
        Gets git and init versions and commits since the init version
        """
        ## get git branch
        self._get_git_branch()

        ## get tag in the init file
        self._get_init_release_tag()

        ## get log commits since <tag>
        try:
            self._get_log_commits()
        except Exception as inst:
            raise Exception(
        """
        Error: the version in __init__.py is {}, so 'git log' is 
        looking for commits that have happened since that version, but
        it appears there is not existing tag for that version. You may
        need to roll back the version in __init__.py to what is actually
        commited. Check with `git tag`.
        --------
        {}
        """.format(self.init_version, inst))

        ## where are we at?
        print("__init__.__version__ == '{}':".format(self.init_version))
        print("'{}' is {} commits ahead of origin/{}"
              .format(self.tag, len(self.commits), self.init_version))



    ## command to run all subfunctions
    def push_git_package(self):
        """
        if no conflicts then write new tag to 
        """
        ## check for conflicts, then write to local files
        self._pull_branch_from_origin()

        ## log commits to releasenotes
        if self.deploy:
            self._write_commits_to_release_notes()

        ## writes tag or 'devel' to 
        try:            
            self._write_new_tag_to_init()
            self._write_branch_and_tag_to_meta_yaml()
            self._push_new_tag_to_git()

        except Exception as inst:
            print("\n Error:\n", inst)
            self._revert_tag_in_init()
            sys.exit(2)



    ## subfunctions ------------------------------------------------
    def _get_git_branch(self):
        """
        checkout the branch
        """
        subprocess.call(["git", "checkout", self.branch])



    def _pull_branch_from_origin(self):
        """
        Pulls from origin/master, if you have unmerged conflicts
        it will raise an exception. You will need to resolve these.
        """
        try:
            ## self.repo.git.pull()
            subprocess.check_call(["git", "pull", "origin", self.branch])
        except Exception as inst:
            sys.exit("""
        Your HEAD commit conflicts with origin/{tag}. 
        Resolve, merge, and rerun versioner.py
        """)



    def _get_init_release_tag(self):
        """
        parses init.py to get previous version
        """
        self.init_version = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                      open(self.init_file, "r").read(),
                                      re.M).group(1)



    def _get_log_commits(self):
        """
        calls git log to complile a change list
        """
        ## check if update is necessary
        cmd = "git log --pretty=oneline {}..".format(self.init_version)
        cmdlist = shlex.split(cmd)
        commits = subprocess.check_output(cmdlist)
        
        ## Split off just the first element, we don't need commit tag
        self.commits = [x.split(" ", 1) for x in commits.split("\n")]



    def _write_commits_to_release_notes(self):
        """
        writes commits to the releasenotes file by appending to the end
        """
        with open(self.release_file, 'a') as out:
            out.write("==========\n{}\n".format(self.tag))
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
        for line in fileinput.input(self.init_file, inplace=1):
            if line.strip().startswith("__version__"):
                line = "__version__ = \"" + self.tag + "\""
            print(line.strip("\n"))        



    def _write_branch_and_tag_to_meta_yaml(self):
        """
        Write branch and tag to meta.yaml by editing in place
        """
        ## set the branch to pull source from
        with open(self.meta_yaml.replace("meta", "template"), 'r') as infile:
            dat = infile.read()
            newdat = dat.format(**{'tag': self.tag, 'branch': self.branch})

        with open(self.meta_yaml, 'w') as outfile:
            outfile.write(newdat)

        # for line in fileinput.input(self.meta_yaml, inplace=1):
        #     if line.strip().startswith("  git_tag: "):
        #         if self.deploy:
        #             line = "  git tag: {}".format(self.tag)
        #         else:
        #             line = "  git tag: {}".format(self.branch)
        #     print(line.strip("\n"))        
        # ## set the tag to use for the package name
        # for line in fileinput.input(self.meta_yaml, inplace=1):
        #     if line.strip().startswith("  version: "):
        #         line = "  version: {}".format(self.tag)
        #     print(line.strip("\n"))        



    def _revert_tag_in_init(self):
        """
        Write version to __init__.py by editing in place
        """
        for line in fileinput.input(self.init_file, inplace=1):
            if line.strip().startswith("__version__"):
                line = "__version__ = \"" + self.init_version + "\""
            print(line.strip("\n"))
        
        print("reverted __init__.__version__ back to {}"
              .format(self.init_version))

        ## remove the tag if it was created
        #subprocess.call(["git", "tag", "-d", self.tag])



    def _push_new_tag_to_git(self):
        """
        tags a new release and pushes to origin/master
        """
        print("Pushing new version to git")            

        ## stage the releasefile and initfileb
        subprocess.call(["git", "add", self.release_file])
        subprocess.call(["git", "add", self.init_file])
        subprocess.call([
            "git", "commit", "-m", "Updating {}/__init__.py to version {}"\
            .format(self.package, self.tag)])

        ## push changes to origin <tracked branch>
        subprocess.call(["git", "push", "origin", self.branch])

        ## create a new tag for the version number on deploy
        if self.deploy:
            subprocess.call([
                "git", "tag", "-a", self.tag,
                "-m", "Updating version to {}".format(self.tag),
                ])
            subprocess.call(["git", "push", "origin"]) 

        #else:
        #    ## temporarily tag this with a test number
        #    subprocess.call(["git", "tag", "-a", "-m", "tmp-test", self.tag])



    ## builds linux and osx 64-bit versions on py27 and py35
    def build_conda_packages(self):
        """
        Run the Linux build and use converter to build OSX
        """
        ## check if update is necessary
        #if self.nversion == self.pversion:
        #    raise SystemExit("Exited: new version == existing version")

        ## tmp dir
        bldir = "./tmp-bld"
        if not os.path.exists(bldir):
            os.makedirs(bldir)

        ## iterate over builds
        for pybuild in ["2.7", "3"]:

            ## build and upload Linux to anaconda.org
            build = api.build(
                "conda-recipe/{}".format(self.package),
                 python=pybuild)
                
            ## upload Linux build
            if not self.deploy:
                cmd = ["anaconda", "upload", build[0], "--label", "test", "--force"]
            else:
                cmd = ["anaconda", "upload", build[0]]
            err = subprocess.Popen(cmd).communicate()

            ## build OSX copies 
            api.convert(build[0], output_dir=bldir, platforms=["osx-64"])
            osxdir = os.path.join(bldir, "osx-64", os.path.basename(build[0]))
            if not self.deploy:
                cmd = ["anaconda", "upload", osxdir, "--label", "test", "--force"]
            else:
                cmd = ["anaconda", "upload", osxdir]
            err = subprocess.Popen(cmd).communicate()

        ## cleanup tmpdir
        shutil.rmtree(bldir)

        ## remove tmp tag if not deploying
        #subprocess.call(["git", "tag", "-d", self.tag])




def parse_command_line():
    """ Parse CLI args."""

    ## create the parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  * Example command-line usage: 

  ## push test branch to conda --label=conda-test for travis CI
  ./versioner.py -p toytree -b test -t 0.1.7 

  ## push master as a new tag to git and conda
  ./versioner.py -p toytree -b master -t 0.1.7 --deploy

  ## build other deps on conda at --label=conda-test
  ./versioner.py -p toyplot --no-git
  ./versioner.py -p pypng --no-git

    """)

    ## add arguments 
    parser.add_argument('-v', '--version', action='version', 
        version="0.1")

    parser.add_argument('-p', #"--package", 
        dest="package", 
        default="toytree",
        type=str, 
        help="the tag to put in __init__ and use on conda")

    parser.add_argument('-b', #"--branch", 
        dest="branch", 
        default="master",
        type=str,
        help="the branch to build conda package from")

    parser.add_argument('-t', #"--tag", 
        dest="tag", 
        default="test",
        type=str, 
        help="the tag to put in __init__ and use on conda")

    parser.add_argument("--deploy", 
        dest="deploy",
        action='store_true',
        help="push the tag to git and upload to conda main label")

    parser.add_argument("--no-git", 
        dest="nogit",
        action='store_true',
        help="skip git update and only build/upload to conda")


    ## if no args then return help message
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    ## parse args
    args = parser.parse_args()
    return args



## MAIN CLI CALL todo add optparse options
if __name__ == "__main__":

    ## parse command-line args
    args = parse_command_line()

    ## init Toytree tag 
    v = Version(args.package, args.branch, args.tag, args.deploy)

    ## push tag or to git
    if not args.nogit:
        if args.package == "toytree":
            v.get_git_status()
            v.push_git_package()
        else:
            raise Exception("git updates code only available for pkg toytree")

    ## build the conda packages and upload
    v.build_conda_packages()

    ## write version back to starting if not a deployed version
    if not args.deploy:
        v._revert_tag_in_init()