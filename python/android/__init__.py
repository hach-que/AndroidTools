#!/usr/bin/env python

from apptools.native import fs
import os
import subprocess
import sys
import shutil
import tarfile
from pyparsing import Literal, Or, Word, printables, alphanums, alphas, LineEnd

CONFIG_PREP_ROOT = "/build/prep"
CONFIG_APP_ROOT = "/data/data/kevinboone.androidterm/kbox/usr"

__all__ = [ "parse_config", "Package" ]

class ConfigureProvider():
    def __init__(self, pkgname):
        # Package name
        self._name = pkgname

        # Define include paths
        self._include_paths = list()
        self._include_paths.append("/build/toolchain/arm-linux-androideabi/include/c++/4.6/")
        self._include_paths.append("/build/toolchain/arm-linux-androideabi/include/c++/4.6/arm-linux-androideabi/")

        # Define linker paths
        self._linker_paths = list()

        # Define linker libraries
        self._linker_libs = list()

        # Define configure parameters
        self._configure_params = list()

        # Define hacks
        self._hacks = list()

    def accept(self, args):
        if (args[0] == "include" and args[1] == "headers"):
            self._include_paths.append(args[2])
        elif (args[0] == "include" and args[1] == "libraries"):
            self._linker_paths.append(args[2])
        elif (args[0] == "link"):
            self._linker_libs.append(args[1])
        elif (args[0] == "option" and args[1] == "configure"):
            self._configure_params.append(args[2])
        elif (args[0] == "option" and args[1] == "hack"):
            self._hacks.append(args[2].lower())
        else:
            raise Exception("unknown entry in configuration file: " + str(args))

    def _execute(self, args):
        p = subprocess.Popen(args, env=self._env)
        p.wait()
        if (p.returncode != 0):
            sys.exit(1)

    def build(self):
        # Create environment variables
        LDFLAGS = ""
        CFLAGS = "-Wno-error"
        CCFLAGS = "-Wno-error"
        CXXFLAGS = "-Wno-error"
        CPPFLAGS = "-Wno-error"
        for i in self._linker_paths:
            LDFLAGS += "-L" + i + " "
        for i in self._linker_libs:
            LDFLAGS += "-l" + i + " "
        for i in self._include_paths:
            CFLAGS += "-I" + i + " "
            CCFLAGS += "-I" + i + " "
            CXXFLAGS += "-I" + i + " "
            CPPFLAGS += "-I" + i + " "

        # Apply hacks
        for i in self._hacks:
            if (i == "localeconv"):
                CFLAGS += "-D__HACK_BUILTIN_LOCALECONV"
                CCFLAGS += "-D__HACK_BUILTIN_LOCALECONV"
                CXXFLAGS += "-D__HACK_BUILTIN_LOCALECONV"
                CPPFLAGS += "-D__HACK_BUILTIN_LOCALECONV"
            else:
                raise Exception("unknown hack '" + i + "' specified in config file")

        # Create enviroment dictionary
        self._env = {
            "LDFLAGS": LDFLAGS,
            "CFLAGS": CFLAGS,
            "CCFLAGS": CCFLAGS,
            "CXXFLAGS": CXXFLAGS,
            "CPPFLAGS": CPPFLAGS,
            "PATH": "/build/toolchain/bin/:" + os.environ["PATH"],
        }

        # Generate configure parameters.
        configure = list()
        configure.append("../src/configure")
        configure.append("--prefix=" + CONFIG_APP_ROOT)
        configure.append("--build=x86_64-unknown-linux-gnu")
        configure.append("--host=arm-linux-androideabi")
        configure.append("--target=arm-linux-androideabi")
        for i in self._configure_params:
            configure.append(i)

        # Execute build.
        self._execute(configure)
        self._execute(["make"])
        self._execute(["make", "install", "DESTDIR=/build/prep/" + self._name + "/install"])

    def get_output(self):
        return "/build/prep/" + self._name + "/install/" + CONFIG_APP_ROOT

class AppToolsProvider():
    def __init__(self, name):
        self._name = name
    
    def package(self, file_path):
        if (os.path.exists(self._name + ".afs")):
            print "Removing old AppTools package..."
            os.unlink(self._name + ".afs")
        print "Creating AppTools package..."
        fs.Package.create(self._name + ".afs", self._name, "Unversioned", "", "")
        pkg = fs.Package(self._name + ".afs")
        for root, folders, files in os.walk(file_path):
            for i in folders:
                pkg.mkdir(os.path.join(root, i)[len(file_path)+1:], 0755)
            for i in files:
                # We don't support reading or writing to files yet in the API.
                pass

class TarProvider():
    def __init__(self, name):
        self._name = name

    def package(self, file_path):
        if (os.path.exists(self._name + ".tar.gz")):
            print "Removing old tar.gz package..."
            os.unlink(self._name + ".tar.gz")
        print "Creating tar.gz package..."
        count = 0
        tar = tarfile.open(self._name + ".tar.gz", "w:gz")
        for root, folders, files in os.walk(file_path):
            for i in folders:
                tar.add(os.path.join(root, i), arcname=os.path.join(root, i)[len(file_path):], recursive=False)
                count += 1
                self.print_status(count)
            for i in files:
                tar.add(os.path.join(root, i), arcname=os.path.join(root, i)[len(file_path):], recursive=False)
                count += 1
                self.print_status(count)
        tar.close()

    def print_status(self, count):
        if (count < 1000 and count % 50 == 0):
            print ".. " + str(count) + " entries added"
        elif (count % 1000 == 0):
            print ".. " + str(count) + " entries added"

class AllProvider():
    def __init__(self, name):
        self._name = name

    def package(self, file_path):
        for i in package_providers:
            if (i == "all"):
                continue
            pp = package_providers[i](self._name)
            pp.package(file_path)

build_providers = {
    "configure": ConfigureProvider
}

package_providers = {
    "apptools": AppToolsProvider,
    "tar": TarProvider,
    "all": AllProvider
}

def parse_config(filename, pkgname):
    result = {}
    result["include_paths"] = list()
    result["linker_paths"] = list()
    result["linker_libs"] = list()

    grammar = ( Literal("type") + Literal("configure") ) | \
              ( Literal("include") + (
                  Literal("headers") | \
                  Literal("libraries") ) + Word(printables + " ") + LineEnd() ) | \
              ( Literal("link") + Word(alphanums) ) | \
              ( Literal("option") + Word(alphas) + Word(printables + " ") + LineEnd() )

    current_type = None

    for l in open(filename):
        l = l.strip()
        if (len(l) == 0):
            continue # Ignore blank lines
        if (l[0] == "#"):
            continue # Ignore lines starting with a hash
        l = l.replace("%ROOT%", CONFIG_APP_ROOT)
        l = l.replace("%PREP%", CONFIG_PREP_ROOT)
        inp = grammar.parseString(l)
        if (inp[0] == "type" and current_type == None):
            current_type = build_providers[inp[1]](pkgname)
        elif (inp[0] == "type" and current_type != None):
            raise Exception("type can not be specified twice")
        elif (current_type == None):
            raise Exception("type must be specified before any other directives")
        else:
            current_type.accept(inp)

    return current_type

class Package():
    def __init__(self, name):
        # Package name
        self._name = str(name)

    def build(self):
        if (os.path.exists(CONFIG_PREP_ROOT + "/" + self._name + "/build")):
            print "Cleaning out existing build folder..."
            shutil.rmtree(CONFIG_PREP_ROOT + "/" + self._name + "/build")
        if (os.path.exists(CONFIG_PREP_ROOT + "/" + self._name + "/install")):
            print "Cleaning out existing install folder..."
            shutil.rmtree(CONFIG_PREP_ROOT + "/" + self._name + "/install")
        os.mkdir(CONFIG_PREP_ROOT + "/" + self._name + "/build")
        os.mkdir(CONFIG_PREP_ROOT + "/" + self._name + "/install")
        print "Changing to build directory..."
        os.chdir(CONFIG_PREP_ROOT + "/" + self._name + "/build")
        provider = parse_config(CONFIG_PREP_ROOT + "/" + self._name + "/config", self._name)
        provider.build()

    def package(self, output_type):
        if (not os.path.exists(CONFIG_PREP_ROOT + "/" + self._name + "/output")):
            os.mkdir(CONFIG_PREP_ROOT + "/" + self._name + "/output")
        print "Changing to output directory..."
        os.chdir(CONFIG_PREP_ROOT + "/" + self._name + "/output")
        build = parse_config(CONFIG_PREP_ROOT + "/" + self._name + "/config", self._name)
        output = package_providers[output_type](self._name)
        output.package(build.get_output())
