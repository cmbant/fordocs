"""
Created on Aug 9, 2014
@author: Mohammed Hamdy
"""

import copy
import fnmatch
import os
import re

from sqlalchemy.exc import NoResultFound

from .parsers import FileParser, ProgramParser
from .source_model import (
    Class,
    ClassSubroutine,
    ClassVariable,
    Dependency,
    File,
    FileSubroutine,
    Generic,
    Interface,
    Module,
    ModuleSubroutine,
    ProgramFile,
    SubroutineArgument,
    createNewDatabase,
    session,
)

NOISY = True


class ModelFiller:
    """
    Walks over all the Fortran source files and, using parsers, fills a database model with parsed
    stuff
    """

    def __init__(self, defines):
        self._defines = defines
        self._processed_files_count = 0

    def fillModel(self, sourceFolders=[], match="*.f90", file_list=[], excludes=[]):
        createNewDatabase()

        if match:
            compiled_regex = re.compile(fnmatch.translate(match), re.IGNORECASE)
        compiled_excludes = [
            re.compile(fnmatch.translate(exclude), re.IGNORECASE)
            for exclude in excludes
        ]

        def excluded(fname):
            for ex in compiled_excludes:
                if ex.match(fname):
                    return True
            return False

        if sourceFolders and isinstance(sourceFolders, str):
            sourceFolders = [sourceFolders]
        for sourceFolder in sourceFolders:
            if not os.path.isdir(sourceFolder):
                raise ValueError(f"Invalid source directory : {sourceFolder}")
            for root, dirs, files in os.walk(sourceFolder, topdown=True):
                for dir in copy.copy(dirs):
                    if dir[0] == "." or excluded(dir):
                        dirs.remove(dir)
                if not excluded(root):
                    for f in files:
                        if compiled_regex.match(f) and not excluded(f):
                            file_list.append(os.path.join(root, f))

        for full_source_path in file_list:
            if NOISY:
                print(f"Parsing {full_source_path}")
            with open(full_source_path) as fhandle:
                source = fhandle.read()
                # both Files and ProgramFiles can contain subroutines
                if ProgramParser.isProgram(source):
                    self._fileFromParser(ProgramParser, full_source_path)
                else:
                    self._fileFromParser(FileParser, full_source_path)
                self._processed_files_count += 1

    def fileCount(self):
        return self._processed_files_count

    def _isFortranSource(self, fname):
        return fname.lower().endswith(".f90")

    def _fileFromParser(self, ParserClass, fullFilename):
        source = open(fullFilename).read()
        parsed_file = ParserClass.parse(source, self._defines)
        if ParserClass == FileParser:
            dbfile = File()
        elif ParserClass == ProgramParser:
            dbfile = ProgramFile()
        dbfile.name = fullFilename
        dbfile.comment = parsed_file.comment
        session.add(dbfile)
        session.commit()
        dbmodules = self._extractModules(parsed_file.modules)
        for module in dbmodules:  # associate the module with it's file
            module.file_id = dbfile.id
        dbdependencies = self._extractDependencies(parsed_file.dependencies)
        dbfile.modules = dbmodules
        dbfile.dependencies = dbdependencies
        dbsubroutines = self._extractSubroutines(parsed_file.subroutines, dbfile)
        for subroutine in dbsubroutines:  # associate subroutines with their dbfile
            subroutine.program_id = dbfile.id
        dbfile.subroutines = dbsubroutines
        session.commit()
        return dbfile, parsed_file

    # All _extract* methods does is convert a parse object to database object.

    def _extractArguments(self, argList, ArgumentClass, extra):
        # extra is either a database Class or Subroutine
        res = []
        for arg in argList:
            argument = ArgumentClass(
                name=arg.name,
                full_name=arg.full_name,
                type=arg.type,
                comment=arg.comment,
                extras=arg.extras,
            )
            # should associate these with a subroutine (in case of a subroutine argument) or a class otherwise
            if ArgumentClass == ClassVariable:
                argument.class_id = extra.id
            elif ArgumentClass == SubroutineArgument:
                argument.subroutine_id = extra.id
            res.append(argument)
        return res

    def _extractSubroutines(self, subroutineList, dbOwner):
        # dbOwner should be a valid database Module, Class or Program, to which the subroutines belong
        if isinstance(dbOwner, (ProgramFile, File)):
            SubroutineSubclass = FileSubroutine
        elif isinstance(dbOwner, Module):
            SubroutineSubclass = ModuleSubroutine
        elif isinstance(dbOwner, Class):
            SubroutineSubclass = ClassSubroutine
        res = []
        for subroutine in subroutineList:
            dbsubroutine = SubroutineSubclass(
                name=subroutine.name,
                alias=subroutine.alias,
                comment=subroutine.comment,
                category=subroutine.category,
                result_name=subroutine.result_name,
                typeString=subroutine.typeString,
            )
            session.add(dbsubroutine)
            session.commit()
            arguments = self._extractArguments(
                subroutine.arguments, SubroutineArgument, dbsubroutine
            )
            dbsubroutine.arguments = arguments
            res.append(dbsubroutine)
        return res

    def _extractClass(self, cls, dbModule):
        # find the class in the database first. Maybe it was found as a parent before it's declaration was found
        dbcls = session.query(Class).filter(Class.name == cls.name).first()
        if not dbcls:
            dbcls = Class(name=cls.name)
        dbcls.access_modifier = cls.access_modifier
        dbcls.module_id = dbModule.id
        dbcls.comment = cls.comment
        dbcls.subroutines = self._extractSubroutines(cls.subroutines, dbcls)
        dbcls.generics = self._extractGenerics(cls.generics)
        session.add(dbcls)
        session.commit()
        dbcls.variables = self._extractArguments(cls.variables, ClassVariable, dbModule)
        return dbcls

    def _extractClasses(self, classList, dbModule):
        # ensures that the parent class at the top of the tree is created first
        # passes it's id to children
        res = []
        for cls in classList:
            dbcls = self._extractClass(cls, dbModule)
            if cls.parent:
                # check that the parent is not in the database first
                parent = session.query(Class).filter(Class.name == cls.parent).first()
                if parent:
                    dbcls.parent_id = parent.id
                else:
                    # a new parent will be created
                    parent = Class(
                        name=cls.parent
                    )  # other attributes are currently unknown
                    session.add(parent)
                    session.commit()
                    dbcls.parent_id = parent.id
            else:
                pass  # leave the class with no parent from database
            res.append(dbcls)
        return res

    def _extractModules(self, moduleList):
        # the owner file should be associated to the results from this method
        res = []
        for module in moduleList:
            # check if any modules in this file are already in the database and not fully initialized.
            # if so, now you know about them from the file and populate them
            try:
                dbmodule = (
                    session.query(Module).filter(Module.name == module.name).one()
                )
            except NoResultFound as _:
                # create a new module and populate it
                dbmodule = Module(name=module.name)
                session.add(dbmodule)
                session.commit()
            dbmodule.comment = module.comment
            dbmodule.dependencies = self._extractDependencies(module.dependencies)
            dbmodule.classes = self._extractClasses(module.classes, dbmodule)
            dbmodule.subroutines = self._extractSubroutines(
                module.subroutines, dbmodule
            )
            dbmodule.interfaces = self._extractInterfaces(module.interfaces, dbmodule)
            for subroutine in dbmodule.subroutines:
                subroutine.module_id = dbmodule.id
            res.append(dbmodule)
        return res

    def _extractDependencies(self, parsedDependencies):
        # ensures that old dependencies are retained and new ones created as necessary
        # (unique constraint is not enforced by sqlalchemy)
        dependencies = []
        for dep in parsedDependencies:
            existing_dependency = (
                session.query(Dependency).filter(Dependency.name == dep).first()
            )
            if existing_dependency:
                dependencies.append(existing_dependency)
            else:
                dependencies.append(Dependency(name=dep))
        return dependencies

    def _extractInterfaces(self, interfaceList, dbModule):
        dbinterfaces = []
        for interface in interfaceList:
            dbinterface = Interface(
                name=interface.name, procedure_names=",".join(interface.procedure_list)
            )
            dbinterface.module_id = dbModule.id
            dbinterfaces.append(dbinterface)
        return dbinterfaces

    def _extractGenerics(self, genericList):
        dbgenerics = []
        for generic in genericList:
            dbgenerics.append(
                Generic(
                    name=generic.name,
                    associated_procedures=generic.associated_procedures,
                )
            )

        return dbgenerics


def startParse(source):
    filler = ModelFiller(source)
    filler.fillModel()
