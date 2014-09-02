'''
Created on Aug 10, 2014
@author: Mohammed Hamdy
'''
from __future__ import print_function
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import func
from source_model import DATABASE_FILE, session, File, ProgramFile, Module, Class,\
  FileSubroutine
from fshandler import FileSystemHandler
import os, sys, re, treelib

env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__),"templates")))
NOISY = True

class HTMLDocMaker(object):
  """
  Read the database into HTML templates
  """
  
  ARGUMENT_CLASS_EXTRACTOR_REGEX = re.compile("(class|type)\s*\((?P<class>\w+)\)", re.IGNORECASE) # also match for things like 'integer'
  
  def __init__(self, destinationDirectory, documentationTitle="Fortran Documentation Index"):
    if not os.path.exists(DATABASE_FILE):
      print("Database file not found. Please run the parse phase <dbmaker.py> first. Exiting")
      sys.exit(1)
    self._fshandler = FileSystemHandler(destinationDirectory)
    env.globals["documentation_title"] = documentationTitle
  
  def makeDocs(self):
    self._fshandler.copyAssets()
    # generate file docs
    self._generateFileDocs()
    # generate program docs
    self._generateProgramDocs()
    # now for modules
    self._generateModuleDocs()
    # classes ...
    self._generateClassDocs()
    # class index
    self._generateClassIndex()
    # main index
    self._generateMainIndex()
    
  def _generateFileDocs(self):
    assets_directory = self._fshandler.assetsDirectory(FileSystemHandler.FROM_FILE_FOLDER)
    home_index = self._fshandler.homeIndex(FileSystemHandler.FROM_FILE_FOLDER)
    class_index = self._fshandler.classIndex(FileSystemHandler.FROM_FILE_FOLDER)
    file_template = env.get_template("file.html")
    dbfiles = session.query(File).all()
    # sort here because it won't help t use order_by on directories
    dbfiles.sort(key=lambda f : self._fshandler.pureFileName(f.name).lower())
    for dbf in dbfiles:
      template_args = self._templateArgsForFile(dbf)
      trees = self._treesForFile(dbf)
      if NOISY:
        print("Rendering template files/{}".format(self._fshandler.htmlNameForPath(dbf.name)))
      out_file_name = self._fshandler.getSaveFileName(dbf.name)
      open(out_file_name, "w").write(
        file_template.render(assets_directory=assets_directory,
                             home_index=home_index,
                             class_index=class_index,
                             file_caption=template_args["file_caption"],
                             file_comment=template_args["file_comment"],
                             modules=template_args["template_modules"],
                             dependencies=template_args["template_dependencies"],
                             subroutines=template_args["template_subroutines"],
                             functions=template_args["template_functions"],
                             trees=trees))
    print()
    
  def _generateProgramDocs(self):
    assets_directory = self._fshandler.assetsDirectory(FileSystemHandler.FROM_PROGRAM_FOLDER)
    home_index = self._fshandler.homeIndex(FileSystemHandler.FROM_PROGRAM_FOLDER)
    class_index = self._fshandler.classIndex(FileSystemHandler.FROM_PROGRAM_FOLDER)
    program_template = env.get_template("program.html")
    dbprograms = session.query(ProgramFile).all()
    dbprograms = sorted(dbprograms, key=lambda program : self._fshandler.pureFileName(program.name).lower())
    for dbprogram in dbprograms:
      template_args = self._templateArgsForFile(dbprogram) # a ProgramFile is the same as File. Difference in template
      if NOISY:
        print("Rendering template programs/{}".format(self._fshandler.htmlNameForPath(dbprogram.name)))
      out_program_name = self._fshandler.getSaveProgramName(dbprogram.name)
      open(out_program_name, 'w').write(
        program_template.render(assets_directory=assets_directory,
                                home_index=home_index,
                                class_index=class_index,
                                program_caption=template_args["file_caption"],
                                program_comment=template_args["file_comment"],
                                modules=template_args["template_modules"],
                                dependencies=template_args["template_dependencies"],
                                subroutines=template_args["template_subroutines"],
                                functions=template_args["template_functions"]))
    print()
    
  def _generateModuleDocs(self):
    assets_directory = self._fshandler.assetsDirectory(FileSystemHandler.FROM_MODULE_FOLDER)
    home_index = self._fshandler.homeIndex(FileSystemHandler.FROM_MODULE_FOLDER)
    class_index = self._fshandler.classIndex(FileSystemHandler.FROM_MODULE_FOLDER)
    module_template = env.get_template("module.html")
    dbmodules = session.query(Module).order_by(Module.name).all()
    for dbmodule in dbmodules:
      module_caption = dbmodule.name
      module_file = session.query(File).filter(File.id==dbmodule.file_id).first()
      module_file_doc = self._fshandler.fileDocForPath(module_file.name, perspective=FileSystemHandler.FROM_MODULE_FOLDER)
      module_file_caption = self._fshandler.pureFileName(module_file.name)
      module_comment = dbmodule.comment
      module_dbclasses = dbmodule.classes
      template_classes = self._parseClasses(module_dbclasses, perspective=FileSystemHandler.FROM_MODULE_FOLDER)
      module_dependencies = dbmodule.dependencies
      template_dependencies = self._parseDependencies(module_dependencies, 
                                                      perspective=FileSystemHandler.FROM_MODULE_FOLDER)
      module_dbsubroutines = dbmodule.subroutines
      template_subroutines, template_functions = self._parseSubroutines(module_dbsubroutines, 
                                                                        perspective=FileSystemHandler.FROM_MODULE_FOLDER)
      module_interfaces = dbmodule.interfaces
      template_interfaces = self._parseInterfaces(module_interfaces)
      trees = self._treesFromClasses(dbmodule.classes, perspective=FileSystemHandler.FROM_MODULE_FOLDER)
      if NOISY:
        print("Rendering template modules/{}".format(self._fshandler.makeHtml(dbmodule.name)))
      output_module_file = self._fshandler.getSaveModuleName(dbmodule.name)
      open(output_module_file, 'w').write(
        module_template.render(assets_directory=assets_directory,
                               home_index=home_index,
                               class_index=class_index,
                               module_caption=module_caption,
                               module_file_doc=module_file_doc,
                               module_file_caption=module_file_caption,
                               module_comment=module_comment,
                               interfaces=template_interfaces,
                               classes=template_classes,
                               dependencies=template_dependencies,
                               subroutines=template_subroutines,
                               functions=template_functions,
                               trees=trees))
    print()
  
  def _generateClassDocs(self):
    assets_directory = self._fshandler.assetsDirectory(FileSystemHandler.FROM_CLASS_FOLDER)
    home_index = self._fshandler.homeIndex(FileSystemHandler.FROM_CLASS_FOLDER)
    class_index = self._fshandler.classIndex(FileSystemHandler.FROM_CLASS_FOLDER)
    class_template = env.get_template("class.html")
    dbclasses = session.query(Class).order_by(Class.name).all()
    for dbclass in dbclasses:
      class_name = dbclass.name
      class_module = dbclass.module
      if class_module:
        class_module_caption = class_module.name
        class_module_doc = self._fshandler.moduleDocForName(class_module.name, 
                                                            perspective=FileSystemHandler.FROM_CLASS_FOLDER)
      else:
        class_module_caption = None
        class_module_doc = None
      class_module = dbclass.module
      if class_module:
        class_file_id = class_module.file_id
        class_file = session.query(File).filter(File.id==class_file_id).first()
        if class_file is not None:
          class_file_caption = self._fshandler.pureFileName(class_file.name)
          class_file_doc = self._fshandler.fileDocForPath(class_file.name, 
                                                          perspective=FileSystemHandler.FROM_MODULE_FOLDER)
        else:
          class_file_caption = None
          class_file_doc = None
      else: # no module, won't find the file
        class_file_caption = None
        class_file_doc = None
      class_comment = dbclass.comment
      class_dbroutines = dbclass.subroutines
      template_subroutines, template_functions = self._parseSubroutines(class_dbroutines, 
                                                                        perspective=FileSystemHandler.FROM_CLASS_FOLDER)
      template_generics = self._parseGenerics(dbclass.generics)
      trees = self._parseTrees([dbclass], perspective=FileSystemHandler.FROM_CLASS_FOLDER) # remember, template requires arrays
      template_properties = self._parseProperties(dbclass.variables)
      class_output_file = self._fshandler.getSaveClassName(dbclass.name)
      if NOISY:
        print("Rendering template classes/{}".format(self._fshandler.makeHtml(dbclass.name)))
      open(class_output_file, 'w').write(
        class_template.render(assets_directory=assets_directory,
                              home_index=home_index,
                              class_index=class_index,
                              class_name=class_name,
                              class_module_caption=class_module_caption,
                              class_module_doc=class_module_doc,
                              class_file_caption=class_file_caption,
                              class_file_doc=class_file_doc,
                              class_comment=class_comment,
                              subroutines=template_subroutines,
                              functions=template_functions,
                              properties=template_properties,
                              generics=template_generics,
                              trees=trees))
    print()
    
  def _generateClassIndex(self):
    # put the class index in the classes directory
    assets_directory = self._fshandler.assetsDirectory(FileSystemHandler.FROM_CLASS_FOLDER)
    home_index = self._fshandler.homeIndex(FileSystemHandler.FROM_CLASS_FOLDER)
    class_index= self._fshandler.classIndex(FileSystemHandler.FROM_CLASS_FOLDER)
    index_doc = self._fshandler.homeIndex(FileSystemHandler.FROM_CLASS_FOLDER)
    output_file_name = self._fshandler.getSaveClassIndexName()
    dbclasses = session.query(Class).order_by(Class.name).all()
    trees = self._parseFullTrees(dbclasses, FileSystemHandler.FROM_CLASS_FOLDER)
    if NOISY:
      print("Rendering template classes/_index.html")
    class_template = env.get_template("class_index.html")
    open(output_file_name, 'w').write(
      class_template.render(assets_directory=assets_directory,
                            home_index=home_index,
                            class_index=class_index,
                            index_doc=index_doc,
                            trees=trees))
    print()
    
  def _generateMainIndex(self):
    output_file_name = self._fshandler.getSaveIndexName()
    assets_directory = self._fshandler.assetsDirectory(FileSystemHandler.FROM_INDEX_FOLDER)
    home_index = self._fshandler.homeIndex(FileSystemHandler.FROM_INDEX_FOLDER)
    class_index= self._fshandler.classIndex(FileSystemHandler.FROM_INDEX_FOLDER)
    dbprograms = session.query(ProgramFile).all()
    dbprograms.sort(key=lambda program:self._fshandler.pureFileName(program.name).lower())
    template_programs = self._parsePrograms(dbprograms, perspective=FileSystemHandler.FROM_INDEX_FOLDER)
    dbfiles = session.query(File).all()
    dbfiles.sort(key=lambda dbfile:self._fshandler.pureFileName(dbfile.name).lower())
    template_files = self._parseFiles(dbfiles, perspective=FileSystemHandler.FROM_INDEX_FOLDER) 
    dbmodules = session.query(Module).all()
    dbmodules.sort(key=lambda dbmodule: dbmodule.name.lower())
    template_modules = self._parseModules(dbmodules, perspective=FileSystemHandler.FROM_INDEX_FOLDER)
    dbclasses = session.query(Class).all()
    dbclasses.sort(key=lambda dbclass:dbclass.name.lower())
    template_classes = self._parseClasses(dbclasses, perspective=FileSystemHandler.FROM_INDEX_FOLDER)
    if NOISY:
      print("Rendering main index")
    index_template = env.get_template("index.html")
    open(output_file_name, 'w').write(
      index_template.render(
        assets_directory=assets_directory,
        home_index=home_index,
        class_index=class_index,
        programs=template_programs,
        files=template_files,
        modules=template_modules,
        classes=template_classes))
    print()
      
  def _getSubroutinesForFile(self, dbFile):
    perspective = self._perspectiveForFile(dbFile)
    file_id = dbFile.id
    dbsubroutines = session.query(FileSubroutine).filter(FileSubroutine.file_id==file_id).all()
    template_subroutines, template_functions = self._parseSubroutines(dbsubroutines, 
                                                                      perspective=perspective)
    return template_subroutines, template_functions
  
  def _parsePrograms(self, dbPrograms, perspective):
    # the output path is adjusted to the main index
    template_programs = []
    for dbprogram in dbPrograms:
      program_path = dbprogram.name
      program_caption = self._fshandler.pureFileName(program_path)
      program_doc = self._fshandler.programDocForPath(program_path, perspective)
      template_programs.append({"caption":program_caption,
                                "doc":program_doc})
    return template_programs
  
  def _parseFiles(self, dbFiles, perspective):
    # like _parsePrograms
    template_files = []
    for dbfile in dbFiles:
      file_caption = self._fshandler.pureFileName(dbfile.name)
      file_doc = self._fshandler.fileDocForPath(dbfile.name, perspective)
      template_files.append({"caption":file_caption,
                             "doc":file_doc})
    return template_files
  
  def _parseModules(self, dbModules, perspective):
    template_modules = []
    for dbmod in dbModules:
      module_name = dbmod.name
      module_caption = module_name
      module_doc = self._fshandler.moduleDocForName(module_name, perspective)
      args = {"caption":module_caption, "doc":module_doc}
      template_modules.append(args)
    return template_modules
  
  def _parseArguments(self, dbSubroutine, perspective):
    template_arguments = []
    dbarguments = dbSubroutine.arguments
    result_name = dbSubroutine.result_name
    for dbarg in dbarguments:
      argument_caption = dbarg.name
      argument_full_caption = dbarg.full_name
      argument_comment = dbarg.comment
      extras = dbarg.extras
      # try to find the class of the argument, if any
      class_doc, class_caption = self._classDocAndCaptionFromType(dbarg.type, perspective)
      if result_name and dbarg.name == result_name:
        is_return = True
        result_name = None
      else:
        is_return = False
      template_arguments.append({"caption":argument_caption, "full_caption":argument_full_caption,
                                  "comment":argument_comment,
                                 "class_doc":class_doc, "class_caption":class_caption,
                                 "extras":extras, "is_return":is_return})
    return template_arguments
  
  def _parseProperties(self, dbProperties, perspective=FileSystemHandler.FROM_CLASS_FOLDER):
    template_properties = []
    for property in dbProperties:
      property_caption = property.full_name
      property_comment = property.comment
      extras = property.extras
      class_doc, class_caption = self._classDocAndCaptionFromType(property.type, perspective)
      template_properties.append({"caption":property_caption, "comment":property_comment,
                                  "class_doc":class_doc, "class_caption":class_caption,
                                  "extras":extras})
    return template_properties
        
  def _parseSubroutines(self, dbSubroutines, perspective):
    template_subroutines = []
    template_functions = []
    for dbsub in dbSubroutines:
      subroutine_caption = "{}({})".format(dbsub.name, 
                                                ", ".join([arg.name for arg in dbsub.arguments]))
      subroutine_comment = dbsub.comment
      # parse arguments and make links to classes where available
      template_arguments = self._parseArguments(dbsub, perspective)
      args = {"caption":subroutine_caption, "comment":subroutine_comment,
                                   "arguments":template_arguments}
      if dbsub.category == "subroutine":
        template_subroutines.append(args)
      elif dbsub.category == "function":
        return_type = dbsub.typeString
        return_doc, return_caption = self._classDocAndCaptionFromType(return_type, perspective)
        args["return_caption"] = return_caption
        args["return_doc"] = return_doc
        template_functions.append(args)
    return template_subroutines, template_functions
  
  def _parseInterfaces(self, dbInterfaces):
    template_interfaces = []
    for dbinterface in dbInterfaces:
      interface_name = dbinterface.name
      procedure_names = dbinterface.procedure_names.split(',')
      template_interfaces.append({"caption":interface_name,
                                  "procedures":procedure_names})
    return template_interfaces
  
  def _parseGenerics(self, dbGenerics):
    template_generics = []
    for dbgen in dbGenerics:
      generic_caption = dbgen.name
      procedure_names = dbgen.associated_procedures.split(',')
      template_generics.append({"caption":generic_caption, "procedure_names":procedure_names})
    return template_generics
  
  def _treeBranchForClass(self, dbClass, perspective):
    # create an inheritance branch by traveling up from dbClass
    originalId = dbClass.id
    currentTree = treelib.Tree()
    currentTree.create_node("Root", "root")
    # climb up to the top-most parent 
    parent_id = dbClass.parent_id
    branch = [dbClass]
    parent_ids = ["root"]
    while parent_id is not None:
      dbclass = session.query(Class).filter(Class.id==parent_id).first()
      branch.insert(0, dbclass) # the branch should start from the top-most parent
      parent_ids.insert(1, dbclass.name) # the ids start at root
      parent_id = dbclass.parent_id
    for (cls, parent_id) in zip(branch, parent_ids):
      self._createTreeNode(currentTree, cls, perspective, parent_id, originalId)
      
    return currentTree, branch # include the branch so you know which classes were "treed"
  
  def _fullTreeForClass(self, dbClass, perspective, currentTree=None, originalId=-1, parentIdentifier="root"):
    # create a the full inheritance tree for dbClass
    included_classes = set()
    if currentTree is None:
      originalId = dbClass.id
      # climb up to the top parent first, then create a tree from there
      parent_id = dbClass.parent_id
      while parent_id is not None:
        dbClass = session.query(Class).filter(Class.id==parent_id).first()
        parent_id = dbClass.parent_id
      # now we are on top
      currentTree = treelib.Tree()
      currentTree.create_node("Root", "root")
      self._createTreeNode(currentTree, dbClass, perspective, "root", originalId)
      included_classes.add(dbClass) # only the first class adds itself
    else:
      self._createTreeNode(currentTree, dbClass, perspective, parentIdentifier, originalId)
    parentIdentifier = dbClass.name 
    dbchildren = session.query(Class).filter(Class.parent_id==dbClass.id).all()
    included_classes.update(dbchildren)
    if dbchildren:
      for dbchild in dbchildren: # when there are no more children, it's over
        _, node_classes = self._fullTreeForClass(dbchild, perspective, currentTree, originalId, parentIdentifier)
        included_classes.update(node_classes)
    return currentTree, included_classes
  
  def _treesFromClasses(self, dbClasses, perspective):
    # create trees that contain only dbClasses, showing relationships between them
    trees = []
    classes_per_tree = []
    dbClasses = set(dbClasses)
    for dbcls in dbClasses:
      class_tree, included_classes = self._treeForClasses(dbcls, dbClasses, perspective)
      if len(included_classes) > 1 and len(included_classes.intersection(dbClasses)) > 1 \
          and not included_classes in classes_per_tree:
        trees.append(class_tree)
        classes_per_tree.append(included_classes)
    return trees
  
  def _treeForClasses(self, aClass, dbClasses, perspective, currentTree=None, parentIdentifier="root"):
    # create a full tree with the exception that only dbClasses are allowed to be in it
    included_classes = set() 
    if currentTree is None:
      # climb up to the top
      parent_id = aClass.parent_id
      while parent_id is not None:
        aClass = session.query(Class).filter(Class.id==parent_id).first()
        parent_id = aClass.parent_id
      # now i'm on top
      currentTree = treelib.Tree()
      currentTree.create_node("Root", "root")
    if aClass in dbClasses:
      self._createTreeNode(currentTree, aClass, perspective, parentIdentifier, originalId=-1) # don't care about originals here
      parentIdentifier = aClass.name
      included_classes.add(aClass)
    children = session.query(Class).filter(Class.parent_id==aClass.id).all()
    for child in children:
      _, included = self._treeForClasses(child, dbClasses, perspective, currentTree, parentIdentifier=parentIdentifier)
      included_classes.update(included)
    return currentTree, included_classes
    
  def _createTreeNode(self, currentTree, dbClass, perspective, parentIdentifier, originalId):
    if originalId == dbClass.id:
      original = True
    else:
      original = False
    currentTree.create_node(dbClass.name, dbClass.name, parent=parentIdentifier, 
                              data=NodeData(self._fshandler.classDocForName(dbClass.name, perspective),
                                            dbClass.name, original))
  
  def _templateModulesForFile(self, dbFile):
    perspective = self._perspectiveForFile(dbFile)
    dbmodules = dbFile.modules
    template_modules = [{"caption":dbmodule.name, "doc":self._fshandler.moduleDocForName(dbmodule.name,
                           perspective=perspective)} for dbmodule in dbmodules]
    return template_modules
  
  def _templateDependenciesForFile(self, dbFile):
    perspective = self._perspectiveForFile(dbFile)
    dbdependencies = dbFile.dependencies
    template_dependencies = self._parseDependencies(dbdependencies, perspective=perspective)
    return template_dependencies
  
  def _parseDependencies(self, dbDependencies, perspective): 
    template_dependencies = []
    # I need to know which dependencies are also modules so I know their definer file
    user_defined_dependencies = session.query(Module)
    for dbdep in dbDependencies:
      dependency_caption = dbdep.name
      # does a dependency have a matching module name and thus a file?. should yield at max one
      user_defined_dependency = user_defined_dependencies.filter(func.lower(Module.name)==func.lower(dbdep.name)).first()
      if user_defined_dependency: 
        dep_fileid = user_defined_dependency.file_id
        definer = session.query(File).filter(File.id==dep_fileid).first()
        if definer is not None:
          definer_caption = self._fshandler.pureFileName(definer.name)
          definer_doc = self._fshandler.fileDocForPath(definer.name, perspective)
          dependency_doc = self._fshandler.moduleDocForName(user_defined_dependency.name, perspective)
        else: # weird
          definer_caption = None
          definer_doc = None
          dependency_doc = None
      else: # maybe a built-in dependency or other
        definer_caption = None
        definer_doc = None
        dependency_doc = None
      template_dependencies.append({"caption":dependency_caption,
                                    "doc":dependency_doc,
                                    "definer": {"caption":definer_caption,
                                                "doc":definer_doc}})
    return template_dependencies
  
  def _parseClasses(self, dbClasses, perspective):
    template_classes = []
    for dbclass in dbClasses:
      class_link = self._fshandler.classDocForName(dbclass.name, perspective)
      class_caption = dbclass.name
      template_classes.append({"link":class_link, "caption":class_caption})
    return template_classes
  
  def _templateArgsForFile(self, dbFile):
    file_caption = self._fshandler.pureFileName(dbFile.name)
    file_comment = dbFile.comment
    template_modules = self._templateModulesForFile(dbFile)
    template_dependencies = self._templateDependenciesForFile(dbFile)
    template_subroutines, template_functions = self._getSubroutinesForFile(dbFile)
    return {"file_caption":file_caption, "file_comment":file_comment,
            "template_dependencies":template_dependencies, "template_subroutines":template_subroutines,
            "template_functions":template_functions, "template_modules":template_modules}
    
  def _treesForFile(self, dbFile):
    # make a tree for each class in the file
    file_dbclasses = session.query(Class).join(Module).filter(Module.file_id==dbFile.id).all()
    trees = self._treesFromClasses(file_dbclasses, perspective=FileSystemHandler.FROM_FILE_FOLDER)
    return trees
  
  def _parseTrees(self, dbClasses, perspective):
    # creates a single branch for every class
    already_included_classes = set()
    branches_trees = []
    for cls in dbClasses:
      if cls not in already_included_classes:
        class_tree, included_classes = self._treeBranchForClass(cls, perspective)
        branches_trees.append((included_classes, class_tree))
        already_included_classes.update(included_classes)
    # keep the longest branch. and any classes that don't belong to it
    longest_branch, corresponding_tree = [], None
    trees = []
    for (branch, tree) in branches_trees:
      if len(branch) > len(longest_branch):
        longest_branch = branch
        corresponding_tree = tree
    if corresponding_tree:
      trees.append(corresponding_tree) # the longest tree should be always drawn
    for (branch, tree) in branches_trees:
      for dbcls in branch:
        if dbcls not in longest_branch: # include it's tree
          trees.append(tree)
          break
    return trees
  
  def _parseFullTrees(self, dbClasses, perspective):
    trees = []
    already_included_classes = set()
    for cls in dbClasses:
      if cls not in already_included_classes:
        class_tree, included_classes = self._fullTreeForClass(cls, perspective, currentTree=None)
        already_included_classes.update(included_classes)
        if len(included_classes) > 1:
          trees.append(class_tree)
    return trees
  
  def _classDocAndCaptionFromType(self, typeString, perspective):
    return_class_extractor_regex = self.ARGUMENT_CLASS_EXTRACTOR_REGEX
    if typeString:
      class_match = return_class_extractor_regex.match(typeString)
      if class_match:
        return_class = class_match.group("class")
        # check it's database entry
        db_return_class = session.query(Class).filter(Class.name==return_class).first()
        if db_return_class:
          class_doc = self._fshandler.classDocForName(db_return_class.name, perspective=perspective)
          class_caption = db_return_class.name
        else:
          class_doc = None
          class_caption = return_class
      else:
        class_doc = None
        class_caption = typeString
    else:
      class_doc = None
      class_caption = None
    return class_doc, class_caption
  
  def _perspectiveForFile(self, dbFile):
    # dbFile is a File or ProgramFile. this method fixes the perspective for both
    if isinstance(dbFile, ProgramFile): # ProgramFile must be tested first, since it's a subclass of File
      perspective = FileSystemHandler.FROM_PROGRAM_FOLDER
    elif isinstance(dbFile, File):
      perspective = FileSystemHandler.FROM_FILE_FOLDER
    return perspective

class NodeData(object):
  def __init__(self, link, caption, originalNode=False):
    # the originality flag is used to denote the class that we meant in the tree
    self.link = link
    self.caption = caption
    self.original = originalNode