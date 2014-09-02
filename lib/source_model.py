'''
Created on Aug 7, 2014
@author: Mohammed Hamdy
'''
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from sqlalchemy.sql.schema import Table

DATABASE_FILE = os.path.join(os.path.dirname(__file__), "sourcedb.db")
engine = create_engine("sqlite:///{}".format(DATABASE_FILE), echo=False)
Session = sessionmaker(bind=engine)
session = Session()
DecBase = declarative_base()

# a file can have many dependencies. A dependency can appear in many files. Many to Many
file_dep_assoc = Table("file_dep_assoc", DecBase.metadata, 
                       Column("file_id", Integer, ForeignKey("file.id"), primary_key=True),
                       Column("dependency_id", Integer, ForeignKey("dependency.id"), primary_key=True))
# a module can have many dependencies. And a dependency can appear in many modules. Many to Many
module_dep_assoc = Table("module_dep_assoc", DecBase.metadata,
                         Column("module_id", Integer, ForeignKey("module.id"), primary_key=True),
                         Column("dependency_id", Integer, ForeignKey("dependency.id"), primary_key=True))

class File(DecBase):
  
  __tablename__ = "file"
  
  id = Column(Integer, primary_key=True)
  name = Column(String) # the file name on disk
  comment = Column(String)
  modules = relationship("Module")
  dependencies = relationship("Dependency", secondary=file_dep_assoc, backref="files")
  subroutines = relationship("FileSubroutine", backref="file")
  # configure table inheritance
  type = Column(String)
  
  __mapper_args__ = {
                     "polymorphic_identity":"file",
                     "polymorphic_on":type}
  
  def __repr__(self):
    return u"<File name={} id={} at {:0x}>".format(self.name, self.id, id(self))
  
class ProgramFile(File):
  """A program file is the same as File but with optional subroutines"""
  
  __tablename__ = "program"
  
  id = Column(Integer, ForeignKey("file.id"), primary_key=True)
  
  __mapper_args__ = {"polymorphic_identity":"program"}
  
  def __repr__(self):
    return u"<ProgramFile name={} id={} at {:0x}>".format(self.name, self.id, id(self))
  
class Dependency(DecBase):
  
  __tablename__ = "dependency"
  
  id = Column(Integer, primary_key=True)
  # non unique because it seems similarly named modules are defined. It may or may not match a module name
  name = Column(String) 
  
  type = Column(String)
  __mapper_args__ = {
                     "polymorphic_identity":"dependency",
                     "polymorphic_on":type}
  
  def __repr__(self):
    return u"<Dependency name={} id={} at {:0x}>".format(self.name, self.id, id(self))
  
class Interface(DecBase):
  """Belong to modules"""
  __tablename__ = "inteface"
  
  id = Column(Integer, primary_key=True)
  name = Column(String)
  procedure_names = Column(String) # comma-separated list of procedure names. Could be complicated by linking to subroutine names. Ain't worth it
  module_id = Column(Integer, ForeignKey("module.id"))
  
  def __repr__(self):
    return "<Interface name={} at {:0x}>".format(self.name, id(self))
  
class Generic(DecBase):
  
  __tablename__ = "generic"
  
  id = Column(Integer, primary_key=True)
  name = Column(String) # the mapper subroutine name
  associated_procedures = Column(String) # comma-separated strings
  class_id = Column(Integer, ForeignKey("class.id"))
  
  def __repr__(self):
    return "<Generic {} at {:0x}>".format(self.name, id(self))
 
class Module(DecBase):
  """Represents a Fortran module"""
  
  __tablename__ = "module"
  
  id = Column(Integer, primary_key=True)
  name = Column(String)
  comment = Column(String)
  file_id = Column(Integer, ForeignKey("file.id"))
  # a dependency won't always have a module. It may've been parsed from a file
  dependencies = relationship("Dependency", secondary=module_dep_assoc, backref="modules")  
  classes = relationship("Class", backref="module") # a module can have classes
  subroutines = relationship("ModuleSubroutine", backref="module")
  interfaces = relationship("Interface", backref="module")
  
  __mapper_args__ = {"polymorphic_identity":"module"}
  
  def __repr__(self):
    return u"<Module name={} id={} at {:0x}>".format(self.name, self.id, id(self))

  
class Class(DecBase):  
  """Represents a Fortran type"""
  
  __tablename__ = "class"
  
  id = Column(Integer, primary_key=True)
  name = Column(String)
  comment = Column(String)
  # Fortran 2003 doesn't support multiple-inheritance, so single parent
  parent_id = Column(Integer, ForeignKey("class.id"))
  access_modifier = Column(String) # private/public...
  # I'll assume each class belongs to a module
  module_id = Column(Integer, ForeignKey("module.id"))
  subroutines = relationship("ClassSubroutine", backref="clazz") # can't use class as column name
  variables = relationship("ClassVariable", backref="clazz")
  generics = relationship("Generic", backref="clazz")
  
  def __eq__(self, other):
    # used in doc maker to check classes already included for inheritance
    return self.name == other.name
  
  def __repr__(self):
    return "<Class name={} id={} at {:0x}>".format(self.name, self.id, id(self))
  
class Subroutine(DecBase):
  """A general subroutine or function. Doesn't belong to a class nor a program"""
  __tablename__ = "subroutine"
  
  id = Column(Integer, primary_key=True)
  name = Column(String)
  alias = Column(String)
  comment = Column(String)
  category = Column(String) # subroutine or function, always lowercase
  result_name = Column(String) # the result name is fetched here
  typeString = Column(String) 
  arguments = relationship("SubroutineArgument", backref="subroutine")
  
  type = Column(String)
  __mapper_args__ = {
                     "polymorphic_identity":"subroutine",
                     "polymorphic_on":type}
  
  def __repr__(self):
    return "<Subroutine name={} id={} at {:0x}>".format(self.name, self.id,
                                                        id(self))
  
class FileSubroutine(Subroutine):
  """Represents a file/program subroutine"""
  
  __tablename__ = "filesub"
  
  id = Column(Integer, ForeignKey("subroutine.id"), primary_key=True)
  file_id = Column(Integer, ForeignKey("file.id"))
  
  __mapper_args__ = {"polymorphic_identity":"filesub"}
  
  def __repr__(self):
    return u"<FileSubroutine name={} id={} at {:0x}>".format(self.name, self.id, id(self))
  
class ClassSubroutine(Subroutine):
  """Represents a class subroutine"""
  
  __tablename__ = "classroutine"
  
  id = Column(Integer, ForeignKey("subroutine.id"), primary_key=True)
  class_id = Column(Integer, ForeignKey("class.id"))
  
  __mapper_args__ = {"polymorphic_identity":"classroutine"}
  
  def __repr__(self):
    return u"<ClassSubroutine name={} id={} at {:0x}>".format(self.name, self.id, id(self))
  
class ModuleSubroutine(Subroutine):
  
  __tablename__ = "moduleroutine"
  
  id = Column(Integer, ForeignKey("subroutine.id"), primary_key=True)
  module_id = Column(Integer, ForeignKey("module.id"))
  
  __mapper_args__ = {"polymorphic_identity":"moduleroutine"}
  
  def __repr__(self):
    return u"<ModuleSubroutine name={} id={} at {:0x}>".format(self.name, self.id, id(self))

class Variable(DecBase):
  """A superclass for class variables and subroutine arguments"""
  
  __tablename__ = "variable"
  
  id = Column(Integer, primary_key=True)
  name = Column(String) # like M
  full_name = Column(String) # like M(this%love) or M(:)
  # an argument can be a parsed type or else (built-in, type from somewhere else...)
  type = Column(String) # i'll set the column type as a string.
  extras = Column(String) # a comma separated stuff after the argument type
  comment = Column(String)
  type_ = Column(String)
  __mapper_args__ = {
                     "polymorphic_identity":"variable",
                     "polymorphic_on":type_}
  
  def __repr__(self):
    return u"<Variable name={} id={} at {:0x}>".format(self.name, self.id, id(self))
  
class ClassVariable(Variable):
  
  __tablename__ = "classvariable"
  
  id = Column(Integer, ForeignKey("variable.id"), primary_key=True)
  class_id = Column(Integer, ForeignKey("class.id"))
  
  __mapper_args__ = {"polymorphic_identity":"classvariable"}
  
  def __repr__(self):
    return u"<ClassVariable name={} id={} at {:0x}>".format(self.name, self.id,
                                                            id(self))
  
class SubroutineArgument(Variable):
  
  __tablename__ = "argument"
  
  id = Column(Integer, ForeignKey("variable.id"), primary_key=True)
  subroutine_id = Column(Integer, ForeignKey("subroutine.id"))
  
  __mapper_args__ = {"polymorphic_identity":"subroutineargument"}
  
  def __repr__(self):
    return u"<SubroutineArgument name={} id={} at {:0x}>".format(self.name, self.id,
                                                                 id(self))
 
def createNewDatabase():
  if os.path.exists(DATABASE_FILE):
    os.remove(DATABASE_FILE) 
  DecBase.metadata.create_all(engine)