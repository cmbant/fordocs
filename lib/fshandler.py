'''
Created on Aug 17, 2014
@author: Mohammed Hamdy
'''

import os.path as pth, shutil, os

class FileSystemHandler(object):
    """
    Isolates DocMaker from handling file system issues. It will utilize relative paths
    to allow copying and pasting docs without breaking it
    """
    
    FROM_FILE_FOLDER = 0
    FROM_PROGRAM_FOLDER = 1
    FROM_CLASS_FOLDER = 2
    FROM_MODULE_FOLDER = 3
    FROM_INDEX_FOLDER = 4
    
    def __init__(self, destinationDirectory):
        if not pth.exists(destinationDirectory): os.makedirs(destinationDirectory)
        if not pth.isdir(destinationDirectory):
            raise ValueError("Invalid directory : {}".format(destinationDirectory))
        self._destination = destinationDirectory
        self.copyAssets()
        self._makeFilesDirectory()
        self._makeProgramsDirectory()
        self._makeClassesDirectory()
        self._makeModulesDirectory()
        
    def copyAssets(self):
        source_assets_directory = self._join(pth.dirname(__file__), "templates/assets")
        output_assets_directory = self._join(self._destination, "assets")
        self._mkDir(output_assets_directory)
        try:
            shutil.rmtree(output_assets_directory)
        except shutil.Error as e:
            print(e)
        else:
            shutil.copytree(source_assets_directory, output_assets_directory)
        
    def homeIndex(self, perspective):
        if perspective == self.FROM_INDEX_FOLDER:
            return "#"
        else:
            return    self._join("..", "index.html")
        
    def classIndex(self, perspective):
        if perspective == self.FROM_CLASS_FOLDER:
            prefix = ''
        elif perspective == self.FROM_INDEX_FOLDER:
            prefix = "classes"
        else:
            prefix = "../classes"
        return    self._join(prefix, "_index.html")  # not that a class named index overwrites the class index
    
    def assetsDirectory(self, perspective):
        if perspective == self.FROM_INDEX_FOLDER:
            prefix = "assets"
        else:
            prefix = "../assets"
        return    prefix
            
    def fileDocForPath(self, filePath, perspective):
        file_doc_name = self.htmlNameForPath(filePath)
        if perspective == self.FROM_FILE_FOLDER:
            prefix = ''
        elif perspective == self.FROM_INDEX_FOLDER:
            prefix = "files"
        else:
            prefix = "../files"
        return    self._join(prefix, file_doc_name)
    
    def programDocForPath(self, programPath, perspective):
        program_doc_name = self.htmlNameForPath(programPath)
        if perspective == self.FROM_PROGRAM_FOLDER:
            prefix = ''
        elif perspective == self.FROM_INDEX_FOLDER:
            prefix = "programs"
        else:
            prefix = "../programs"
            
        return    self._join(prefix, program_doc_name)
    
    def moduleDocForName(self, moduleName, perspective):
        module_doc = self.makeHtml(moduleName)
        if perspective == self.FROM_MODULE_FOLDER:
            prefix = ''
        elif perspective == self.FROM_INDEX_FOLDER:
            prefix = "modules"
        else:
            prefix = "../modules"
            
        return    self._join(prefix, module_doc)
    
    def classDocForName(self, className, perspective):
        class_doc = self.makeHtml(className)
        if perspective == self.FROM_CLASS_FOLDER:
            prefix = ''
        elif perspective == self.FROM_INDEX_FOLDER:
            prefix = "classes"
        else:
            prefix = "../classes"
            
        return    self._join(prefix, class_doc)
    
    def pureFileName(self, filePath):
        file_only = pth.split(filePath)[1]
        return pth.splitext(file_only)[0]
    
    def htmlNameForPath(self, filePath):
        pure_file_name = self.pureFileName(filePath)
        return self.makeHtml(pure_file_name)
    
    def getSaveFileName(self, filePath):
        html_file = self.htmlNameForPath(filePath)
        return self._join(self.files_directory, html_file)
    
    def getSaveProgramName(self, programPath):
        html_program = self.htmlNameForPath(programPath)
        return self._join(self.programs_directory, html_program)
    
    def getSaveClassName(self, className):
        html_class = self.makeHtml(className)
        return self._join(self.classes_directory, html_class)
    
    def getSaveModuleName(self, moduleName):
        html_module = self.makeHtml(moduleName)
        return self._join(self.modules_directory, html_module)
    
    def getSaveIndexName(self):
        return self._join(self._destination, "index.html")
    
    def getSaveClassIndexName(self):
        return self._join(self.classes_directory, "_index.html")
    
    def _makeFilesDirectory(self):
        files_directory = self._join(self._destination, "files")
        self.files_directory = files_directory
        self._mkDir(files_directory)
    
    def _makeProgramsDirectory(self):
        programs_directory = self._join(self._destination, "programs")
        self.programs_directory = programs_directory
        self._mkDir(programs_directory)
    
    def _makeModulesDirectory(self):
        modules_directory = self._join(self._destination, "modules")
        self.modules_directory = modules_directory
        self._mkDir(modules_directory)
    
    def _makeClassesDirectory(self):
        classes_directory = self._join(self._destination, "classes")
        self.classes_directory = classes_directory
        self._mkDir(classes_directory)
    
    def _join(self,p1,p2):
        #Make sure we use / in web links even if generating on Windows
        return pth.join(p1,p2).replace(os.sep,'/')
    
    def _mkDir(self, dirName):
        if not pth.exists(dirName):
            os.mkdir(dirName)
    
    def makeHtml(self, name):
        return name + ".html"
