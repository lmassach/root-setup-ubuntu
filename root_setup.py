#!/usr/bin/env python3
"""
ROOT setup script for Ubuntu-based distributions.

The script clones the ROOT git repository (latest-stable branch) and
compiles ROOT.
"""
import os
import sys
import re
import argparse
import subprocess
import shutil

# import lsb_release

SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
IS_LOCAL_INSTALL = os.path.isfile(os.path.join(SCRIPT_DIR, ".root_setup_py"))
DEPENDENCIES = [
    "dpkg-dev", "cmake", "g++", "gcc", "binutils", "libx11-dev", "libxpm-dev",
    "libxft-dev", "libxext-dev", "python3", "libssl-dev", "gfortran",
    "libpcre3-dev", "libglu1-mesa-dev", "libglew-dev", "libftgl-dev",
    "libmysqlclient-dev", "libfftw3-dev", "libcfitsio-dev", "libgraphviz-dev",
    "libavahi-compat-libdnssd-dev", "libldap2-dev", "python3-dev",
    "libxml2-dev", "libkrb5-dev", "libgsl-dev"
]
CMAKE_FLAGS = ["-DCMAKE_CXX_STANDARD=17"]


def run(*args, check=True, cwd=None, timeout=None, capture=False):
    cp = subprocess.run(
        args, check=check, cwd=cwd, timeout=timeout,
        stdout=(subprocess.PIPE if capture else None),
        encoding=("utf8" if capture else None))
    if capture:
        return cp.stdout


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-d", "--install-dir", type=os.path.abspath,
                        default=(SCRIPT_DIR if IS_LOCAL_INSTALL
                                 else os.path.join(os.environ['HOME'], "root")),
                        help="Installation directory. Default is $HOME/root,"
                              " or the script's directory if an installation"
                              " is already present there.")
    parser.add_argument("-b", "--branch", default="latest-stable",
                        help="Branch of the ROOT git repo to use (default"
                             " latest-stable).")
    parser.add_argument("-j", type=int, default=min(8, os.cpu_count()),
                        help="Number of concurrent processes (default is the"
                        " number of processors, but no more than 8).")
    parser.add_argument("--clean", action="store_true",
                        help="Remove old build and install directories before building.")
    args = parser.parse_args()

    print(f"Cd'ing into install directory {args.install_dir}")
    os.makedirs(args.install_dir, exist_ok=True)
    os.chdir(args.install_dir)

    if os.path.isdir("root"):
        if not os.path.isdir("root/.git"):
            print("FATAL Found a root directory, but it is not a git repo.")
            sys.exit(1)
        print("Previous installation found")
        if not os.path.isfile("root_setup.py") \
            or not os.path.samefile("root_setup.py", SCRIPT_PATH):
            print("Updating local copy of root_setup.py.")
            shutil.copy(SCRIPT_PATH, "./root_setup.py")
        print("Updating repo")
        run("git", "fetch", cwd="./root")
        run("git", "checkout", args.branch, cwd="./root")
        try:
            run("git", "pull", cwd="./root")
        except subprocess.CalledProcessError:
            print("Could not git-pull. This may happen if github is unreachable")
            print("or if the branch given with -b is a tag.")
            print("Trying to compile anyway.")
    else:
        print("No previous installation found, making a new one")
        shutil.copy(SCRIPT_PATH, "./root_setup.py")
        run("git", "clone", "--branch", args.branch,
            "https://github.com/root-project/root.git")

    print("Preparing build")
    if args.clean:
        if os.path.isdir("./build"):
            print("Clean: removing old build directory...")
            shutil.rmtree("./build")
        if os.path.isdir("./install"):
            print("Clean: removing old install directory...")
            shutil.rmtree("./install")
    os.makedirs("./build", exist_ok=True)
    os.makedirs("./install", exist_ok=True)

    # release = lsb_release.get_distro_information()['RELEASE']
    # print(f"Checking Ubuntu version... {release} found")
    # TODO If any dependency package changes name across releases, use
    # the lines above to select a dependency list based on the release

    print("Checking dependencies")
    packages = run("apt", "list", "--installed", capture=True)
    packages = [m[1] for m in re.finditer(r"(?:^|\n)(.+?)\/", packages)]
    missing = [x for x in DEPENDENCIES if x not in packages]
    if missing:
        print(f"Installing missing dependencies: {' '.join(missing)}")
        print("You may want to run an update/full-upgrade first")
        run("sudo", "apt", "-y", "install", *missing)

    print("Checking if additional CMAKE flags are needed")
    packages = run("apt", "list", "--installed", capture=True)
    packages = [m[1] for m in re.finditer(r"(?:^|\n)(.+?)\/", packages)]
    if "libssl3" in packages:
        CMAKE_FLAGS.append("-DWITH_OPENSSL3=TRUE")

    print("Compiling (may take a while)")
    run("cmake", "-DCMAKE_INSTALL_PREFIX=../install", *CMAKE_FLAGS, "../root",
        cwd="./build")
    run("cmake", "--build", ".", "--target", "install", f"-j{args.j:d}",
        cwd="./build")

    print("Done, remember to add a line like this to your .bashrc/.zshrc")
    print(f"alias sroot='source {args.install_dir}/install/bin/thisroot.sh'")
