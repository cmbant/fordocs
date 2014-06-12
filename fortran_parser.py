from treelib import *
import re
import json


class types_parser():
    
    TYPES_REGEX = \
        re.compile('^type,*\s+(?:(?:abstract|private)[,\s]*)*'
                   '(?P<spec>extends\(\s*(?P<superclass>\w+)\s*\))?'
                   '\s*(?:::)?\s*(?P<class_name>\w+)',
                   flags=re.IGNORECASE)

    END_TYPE_REGEX = \
        re.compile('end\s+type', flags=re.IGNORECASE)

    types = { }
    type_inheritance_paths = [ ]

    current_class = None
    reading_vars = True
    current_class_vars = [ ]
    current_class_procs = [ ]
    current_class_comments = [ ]
    var_started = False

    class_data = { }

    # Public Methods
    def read_file(self, module_name, line, current_module):

        if line.strip().upper().startswith('TYPE') and \
            ' IS' not in line.upper() and \
            self.current_class == None:
            res = self.TYPES_REGEX.match(line.strip())
            if (res != None):
                self.current_class = res.group('class_name')

                if res.group('spec') != None and 'extends' in res.group('spec'):
                    self.types[res.group('class_name')] = \
                        { 'file_name' : module_name, 'superclass' : res.group('superclass') }
                else:
                    self.types[res.group('class_name')] = \
                        { 'file_name' : module_name, 'superclass' : None }

        elif self.END_TYPE_REGEX.match(line.strip().upper()) != None:
            self.class_data[self.current_class] = \
                { 'class_in_module' : current_module,
                  'class_vars' : self.current_class_vars,
                  'class_procs' : self.current_class_procs,
                  'class_comments' : self.current_class_comments }

            self.current_class_vars = [ ]
            self.current_class_procs = [ ]
            self.current_class_comments = [ ]
            self.reading_vars = True
            self.current_class = None
            self.var_started = False

        elif self.current_class != None and line.strip().upper().startswith('CONTAINS'):
            self.reading_vars = False

        elif self.current_class != None:
            stripped_line = line.strip()

            if stripped_line != '':
                if self.reading_vars:
                    if stripped_line.startswith('!') and not self.var_started:
                        res = re.match('^[!]+[!\s]*(?P<comment>.+)$', stripped_line)
                        self.current_class_comments.append(res.group('comment'))
                    elif not stripped_line.startswith('!'):
                        line_vars = analyseVariables(stripped_line)
                        for line_var in line_vars:
                            self.var_started = True
                            self.current_class_vars.append(line_var)

                else:
                    proc = self.convert_procedure_line(stripped_line)
                    if proc != None:
                        self.current_class_procs.append(proc)

    def convert_procedure_line(self, line):

        # Remove inline comments (if any)
        if '!' in line:
            line = line[:line.find('!')].strip()

        match = \
            re.match(
                '((?P<type>procedure|generic|final)(,\s+\w+)?\s*(::)?(\s*(?P<proc_des>\w+)\s*=>)?\s*(?P<proc_name>.*))',
                line,
                re.IGNORECASE)

        if (match != None):
            if match.group('proc_des') != None:
                if (match.group('type') == 'generic'):
                    generic_mapping = [f.strip() for f in match.group('proc_name').split(',')]

                    return {
                        'proc_name' : generic_mapping,
                        'proc_des' : match.group('proc_des'),
                        'proc_type' : match.group('type')
                    }
                else:
                    return {
                        'proc_name' : match.group('proc_name'),
                        'proc_des' : match.group('proc_des'),
                        'proc_type' : match.group('type')
                    }
            else:
                return {
                    'proc_name' : match.group('proc_name'),
                    'proc_des' : None,
                    'proc_type' : match.group('type')}

        return None

    def generate(self):
        self.generateInheritancePaths()

    def getClassesForModule(self, module_name):
        type_names = [ ]
        for ty in self.class_data:
            if self.class_data[ty]['class_in_module'] == module_name:
                type_names.append(ty)

        return type_names

    def getTypeNamesForFilename(self, file_name):
        type_names = [ ]
        for ty in self.types:
            if self.types[ty]['file_name'].startswith(file_name):
                type_names.append(ty)

        return type_names
        
    # Private API
    def generateInheritancePaths(self):
        for ty in self.types:
            type_inheritance = [ { ty : self.types[ty]['file_name'] } ]
        
            if self.types[ty]['superclass'] != None:
                superclass = self.safeGetKey(self.types[ty], 'superclass')
                superclass_filename = self.safeGetKey(self.types[ty], 'file_name')

                while superclass != None:
                    type_inheritance.append( { superclass : superclass_filename } )
                    superclass = self.safeGetKey(self.safeGetKey(self.types, superclass), 'superclass')
                    superclass_filename = self.safeGetKey(self.safeGetKey(self.types, superclass), 'file_name')

                # Reverse the list
                type_inheritance = type_inheritance[::-1]
                self.type_inheritance_paths.append(type_inheritance)

    def createTreeForType(self, type_name):
        roots = self.getRoots()
        trees = [ ]

        for root in roots:
            tree = Tree()
            current_path_list = \
                filter(lambda k: k[0].has_key(root) and k[len(k)-1].has_key(type_name), self.type_inheritance_paths)

            if (current_path_list != [ ]):
                # Create root object
                tree.create_node(root, root)

                for path in current_path_list:
                    for i in range(1, len(path)):
                        class_name = str(path[i].keys()[0])
                        parent_class_name = str(path[i-1].keys()[0])
                        class_path = path[i][class_name]

                        if tree.get_node(class_name) is None:
                            tree.create_node(class_name, class_name, parent=parent_class_name, data=class_path)

                trees.append(json.loads(tree.to_json()))

        if trees == [ ]:
            return None

        return trees


    def createTrees(self, file_name):
        roots = self.getRoots()
        trees = [ ]

        for root in roots:
            tree = Tree()
            current_path_list = \
                filter(lambda k: k[0].has_key(root) and file_name in k[len(k)-1].values()[0], self.type_inheritance_paths)

            if (current_path_list != [ ]):
                # Create root object
                tree.create_node(root, root)

                for path in current_path_list:
                    for i in range(1, len(path)):
                        class_name = str(path[i].keys()[0])
                        parent_class_name = str(path[i-1].keys()[0])
                        class_path = path[i][class_name]

                        if tree.get_node(class_name) is None:
                            tree.create_node(class_name, class_name, parent=parent_class_name, data=class_path)

                trees.append(json.loads(tree.to_json()))

        if trees == [ ]:
            return None

        return trees
    
    def getRoots(self):
        roots = [ ]
        for path in self.type_inheritance_paths:
            class_name = str((path[0].keys()[0]))
            roots.append(class_name)
    
        return list(set(roots))
    
    
    # Utility Methods
    @staticmethod
    def safeGetKey(dic, key):
        if dic != None and dic.has_key(key):
            return dic[key]
        else:
            return None    
            
class dependencies_parser():
    USE_REGEX = re.compile('use(,\s+(?:intrinsic|non_intrinsic))?\s*(?:::)?\s+(?P<using>\w+)', flags=re.IGNORECASE)

    usage_dict = { }

    def read_file(self, file_name, line, current_module, module_mapping, program_mapping):
        if line.strip().upper().startswith('USE'):

            # Remove inline comments (if any)
            if '!' in line:
                line = line[:line.find('!')].strip()

            res = self.USE_REGEX.match(line.strip())
            if (res != None):

                defined_in = \
                    module_mapping[res.group('using')] if module_mapping.has_key(res.group('using')) else 'Unknown'

                defined_file_type = 'program' if defined_in in program_mapping else 'file'

                if self.usage_dict.has_key(file_name):
                    self.usage_dict[file_name].append(
                        { 'using' : res.group('using'),
                          'defined_in' : defined_in,
                          'defined_file_type' : defined_file_type,
                          'use_module' : current_module } )
                else:
                    self.usage_dict[file_name] = [
                        { 'using' : res.group('using'),
                          'defined_in' : defined_in,
                          'defined_file_type' : defined_file_type,
                          'use_module' : current_module } ]


    def getDependenciesForFilename(self, file_name):
        if self.usage_dict.has_key(file_name):
            return self.usage_dict[file_name]
        else:
            return [ ]


class subroutine_parser():

    types = 'recursive|logical|integer|real\(.*\)|complex\(.*\)|type\(.*\)'

    SUBROUTINE_REGEX = re.compile('((' + types + ')?\W?)subroutine\s*(?P<name>.*)', flags=re.IGNORECASE)
    FUNCTION_REGEX = re.compile('((' + types + ')?\W?)function\s*(?P<name>.*)', flags=re.IGNORECASE)
    MOD_PROC_REGEX = re.compile('module\s+procedure(?P<mod_procs>.*)', flags=re.IGNORECASE)

    sub_dict = { }
    current_sub = None
    sub_arguments = [ ]
    sub_data = { }

    var_list = [ ]
    comment_list = [ ]
    vars_started = False
    extracted_arguments = [ ]

    def __init__(self):
        self.var_list = [ ]
        self.comment_list = [ ]
        self.extracted_arguments = [ ]
        self.sub_arguments = [ ]
        self.current_sub = None
        self.vars_started = False


    def get_sub_data(self, sub_name):
        if self.sub_data.has_key(sub_name):
            return self.sub_data[sub_name]
        else:
            return { 'vars': [ ],
                     'comments' : [ ] }

    def read_file(self, file_name, line, current_module, current_interface):

        stripped_line = line.strip()
        if ('SUBROUTINE' in stripped_line.upper() or \
            'FUNCTION' in stripped_line.upper()) and \
            not stripped_line.upper().startswith('END') and \
            not stripped_line.startswith('!'):

            res = self.SUBROUTINE_REGEX.match(line.strip())
            if res == None:
                res = self.FUNCTION_REGEX.match(line.strip())

            if (res != None):
                if self.sub_dict.has_key(file_name):
                    self.sub_dict[file_name].append( { 'sub_name' : res.group('name'), 'sub_module' : current_module } )
                else:
                    self.sub_dict[file_name] = [ { 'sub_name' : res.group('name'), 'sub_module' : current_module } ]

                args = \
                    (re.match('([\s\w]+)(?P<arguments>\((?P<clean_args>.*?)\))(\s+result\((?P<ret_args>.*)\))?',
                              res.group('name'),
                              re.IGNORECASE))

                self.extracted_arguments = [ ]
                if args != None and args.group('clean_args') != '':
                    splitted_args = args.group('clean_args').split(',')
                    self.extracted_arguments += [f.strip() for f in splitted_args]

                if args != None and args.group('ret_args') != None:
                    splitted_args = args.group('ret_args').split(',')
                    self.extracted_arguments += [f.strip() for f in splitted_args]

                self.current_sub = res.group('name')

        elif current_interface != None:
            match = self.MOD_PROC_REGEX.match(stripped_line)
            if match != None:
                proc_list = [f.strip() for f in match.group('mod_procs').split(',')]
                if self.sub_dict.has_key(file_name):
                    self.sub_dict[file_name].append(
                        { 'sub_name' : current_interface,
                          'int_procs' : proc_list,
                          'sub_module' : current_module } )
                else:
                    self.sub_dict[file_name] = [
                        { 'sub_name' : current_interface,
                          'int_procs' : proc_list,
                          'sub_module' : current_module } ]


        elif stripped_line.upper().startswith('END') and \
            re.match('end\s+(?:function|subroutine)', stripped_line, re.IGNORECASE) != None:

            self.sub_data[self.current_sub] = \
                { 'vars': self.var_list,
                  'comments': self.comment_list }

            self.current_sub = None
            self.vars_started = False
            self.var_list = [ ]
            self.comment_list = [ ]
            self.extracted_arguments = [ ]

        elif self.current_sub != None:

            if stripped_line.startswith('!'):
                if not self.vars_started:
                    self.comment_list.append(stripped_line[1:])
            else:
                self.vars_started = True
                line_vars = analyseVariables(stripped_line)
                for var in line_vars:
                    for arg in self.extracted_arguments:
                        if var['var_name'].startswith(arg):
                            self.extracted_arguments.remove(arg)
                            self.var_list.append(var)


    def getSubroutinesForFilename(self, file_name):
        if self.sub_dict.has_key(file_name):
            return self.sub_dict[file_name]
        else:
            return [ ]


def analyseVariables(var_line):

    VARIABLE_DEF_REGEX = re.compile('(?P<type>class|type)\s*\((?P<name>\w+?)\).*', re.IGNORECASE)
    VARIABLE_LIST_REGEX = re.compile("(?:(?P<var_name>\w[\=\w\s\.\'\*]*(?:\(.*?\))?'?)(?:,|\Z))", re.IGNORECASE)

    var_class = None
    var_array = [ ]

    if '::' in var_line:
        var_part = var_line[var_line.rfind('::')+2:]
        def_part = var_line[:var_line.rfind('::')]
    else:
        var_part = var_line[var_line.find(' ')+1:]
        def_part = var_line[:var_line.find(' ')]

    # Remove inline comments
    if '!' in var_part:
        var_part = var_part[:var_part.find('!')].strip()

    res = VARIABLE_LIST_REGEX.finditer(var_part)
    var_part = [ ]
    for var_match in res:
        var_part.append(var_match.group('var_name'))


    res = VARIABLE_DEF_REGEX.match(def_part)
    if res != None:
        var_class = res.group('name') # This is a class/type

    for var in var_part:
        if var_class != None:
            var_array.append(
                { 'var_class': var_class,
                  'var_name' : var,
                  'class_type' : res.group('type') })
        else:
            var_array.append(
                { 'var_type': def_part,
                  'var_name': var,
                  'class_type': 'builtin' })

    return var_array
