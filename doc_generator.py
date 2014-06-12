from fortran_parser import *
from jinja2 import Environment, FileSystemLoader
import re
import os
import fnmatch



class doc_generator():

    tparser = types_parser()
    output_path = '.'
    program_name = ''
    module_to_file_mapping = { }
    program_files = [ ]

    def __init__(self):
        scriptFolder = os.path.dirname(os.path.abspath(__file__))
        self.jinjaEnv = Environment(loader=FileSystemLoader(scriptFolder))
        self.index_template = self.jinjaEnv.get_template('index_template.html')
        self.class_template = self.jinjaEnv.get_template('class_template.html')
        self.module_template = self.jinjaEnv.get_template('module_template.html')
        self.file_template = self.jinjaEnv.get_template('file_template.html')
        self.docs_title = 'Fortran Documentation'
        self.defines=[]

    def generate_index(self, output_path):
        listing = os.listdir(output_path)
        filtered_file_list = [f for f in listing if os.path.splitext(f)[1] == '.html' ]

        program_list = [ ]
        file_list = [ ]
        module_list = [ ]
        class_list = [ ]

        filename_regex = re.compile('\w+?_(?P<name>.+).html', re.IGNORECASE)

        for work_file in filtered_file_list:
            if work_file.startswith('program_'):
                program_list.append(filename_regex.match(work_file).group('name'))
            elif work_file.startswith('file_'):
                file_list.append(filename_regex.match(work_file).group('name'))
            elif work_file.startswith('module_'):
                module_list.append(filename_regex.match(work_file).group('name'))
            elif work_file.startswith('class_'):
                class_list.append(filename_regex.match(work_file).group('name'))


        with file(os.path.join(self.output_path, 'index.html'), 'w') as output_file:
            output_file.write(
                self.index_template.render(docs_title = self.docs_title, program_list=program_list,
                                           file_list=file_list,
                                           module_list=module_list,
                                           class_list=class_list))



    def generate_docs(self, source_path, match_pattern, output_path, title=None, conditional_defines=None):
        self.output_path = output_path
        if conditional_defines is not None: self.defines=conditional_defines
        if title is not None: self.docs_title = title

        file_list = [ ]
        compiled_regex = re.compile(fnmatch.translate(match_pattern), re.IGNORECASE)
        for root, dirs, files in os.walk(source_path, topdown=True):
            file_list += [os.path.join(root, j) for j in files if compiled_regex.match(j)]

        print 'Generating modules mapping...'
        self.generateMappings(file_list)

        for work_file in file_list:
            print 'Processing File: ' + work_file
            self.filename_only = os.path.split(work_file)[1]
            self.readFile(work_file)
            is_program = (self.filename_only in self.program_files)

            for module in self.file_module_list:
                classes_in_module = self.tparser.getClassesForModule(module)
                self.subs_in_classes = [ ]

                for cls in classes_in_module:
                    self.generateClassDocumentation(cls, module, is_program)

                self.generateModuleDocumentation(module, is_program)

            self.generateFileDocumentation(work_file, is_program)


    def generateMappings(self, file_list):
        for work_file in file_list:
            f = file(work_file)
            for ln in f:
                line = ln.strip()
                if line.upper().startswith('MODULE'):
                    match = re.match('module\s+(?!procedure)(?P<mod_name>\w+)', line, flags=re.IGNORECASE)
                    if match != None:
                        self.module_to_file_mapping[match.group('mod_name')] = os.path.split(work_file)[1]

                elif line.upper().startswith('PROGRAM'):
                    match = re.match('program\s+(?P<prog_name>\w+)', line, flags=re.IGNORECASE)
                    if match != None:
                        self.program_files.append(os.path.split(work_file)[1])

            f.close()


    def parse_conditionals(self,text):
        def eval_conditional(matchobj):
            statement = matchobj.groups()[1].split('#else')
            statement.append('') # in case there was no else statement
            if matchobj.groups()[0] in self.defines: return statement[0]
            else: return statement[1]

        pattern = r'#ifdef\s*(\S*)\s*((?:.(?!#if|#endif))*.)#endif'
        regex = re.compile(pattern, re.DOTALL)
        while True:
            if not regex.search(text): break
            text = regex.sub(eval_conditional, text)
        return text

    def readFile(self, work_file):
        with file(work_file, 'r') as f:
            lines = self.parse_conditionals(f.read()).splitlines()

        self.sparser = subroutine_parser()
        self.dparser = dependencies_parser()
        self.file_module_list = [ ]

        self.current_module = None
        self.current_interface = None
        cont_line = ''
        for line in lines:
            ln = line.strip()

            # Remove preprocessor lines
            if not ln.startswith('#'):
                if ln.upper().startswith('MODULE'):
                    match = re.match('module\s+(?!procedure)(?P<mod_name>\w+)', ln, flags=re.IGNORECASE)
                    if match != None:
                        self.current_module = match.group('mod_name')
                        self.file_module_list.append(self.current_module)

                elif ln.upper().startswith('END') and re.match('end\s+module', ln, re.IGNORECASE) != None:
                    self.current_module = None

                elif ln.upper().startswith('INTERFACE'):
                    match = re.match('interface\s+(?P<int_name>\w+)', ln, flags=re.IGNORECASE)
                    if match != None:
                        self.current_interface = match.group('int_name')

                elif ln.upper().startswith('END') and re.match('end\s+interface', ln, re.IGNORECASE) != None:
                    self.current_interface = None

                if ln.endswith('&'):
                    if ln.startswith('&'):
                        cont_line += ln[1:-2]
                    else:
                        cont_line += ln[:-2]
                else:
                    if cont_line != '':
                        cont_line += ln if not ln.startswith('&') else ln[1:]

                        self.sparser.read_file(work_file, cont_line, self.current_module, self.current_interface)

                        self.dparser.read_file(
                            work_file, cont_line, self.current_module, self.module_to_file_mapping, self.program_files)

                        self.tparser.read_file(work_file, cont_line, self.current_module)
                        cont_line = ''
                    else:
                        self.sparser.read_file(work_file, line, self.current_module, self.current_interface)

                        self.dparser.read_file(
                            work_file, line, self.current_module, self.module_to_file_mapping, self.program_files)

                        self.tparser.read_file(work_file, line, self.current_module)



        self.tparser.generate()

        self.deps = self.dparser.getDependenciesForFilename(work_file)
        self.subs = self.sparser.getSubroutinesForFilename(work_file)

  

    def generateFileDocumentation(self, work_file, is_program):
        file_subs = filter(lambda k: k['sub_module'] is None, self.subs)

        for file_sub in file_subs:
            file_sub['sub_args'] = self.sparser.get_sub_data(file_sub['sub_name'])['vars']
            file_sub['sub_comments'] = self.sparser.get_sub_data(file_sub['sub_name'])['comments']

        prefix = 'file_'
        if is_program:
            prefix = 'program_'

        output_file = file(os.path.join(self.output_path, prefix + self.filename_only + '.html'), 'w')

        file_dep_list = [dict(t) for t in set([tuple(d.items()) for d in self.deps])]
        inheritance_graph = self.tparser.createTrees(work_file)

        output_file.write(
            self.file_template.render(docs_title = self.docs_title, file_name=self.filename_only,
                            is_program=is_program,
                            sub_list=file_subs,
                            dep_list=file_dep_list,
                            mod_list=self.file_module_list,
                            type_trees=inheritance_graph))

        output_file.flush()
        output_file.close()


    def generateModuleDocumentation(self, module, is_root_program):
        sub_list = [s['sub_name'] for s in self.subs_in_classes]
        module_subs = [s for s in self.subs if s['sub_name'] not in sub_list and s['sub_module'] is module]

        for mod_sub in module_subs:
            mod_sub['sub_args'] = self.sparser.get_sub_data(mod_sub['sub_name'])['vars']
            mod_sub['sub_comments'] = self.sparser.get_sub_data(mod_sub['sub_name'])['comments']

        output_file = file(os.path.join(self.output_path, 'module_' + module.lower() + '.html'), 'w')

        cls_list = self.tparser.getClassesForModule(module)
        dep_list = [s for s in self.deps if s['use_module'] is module]

        # remove duplicates
        dep_list = [dict(t) for t in set([tuple(d.items()) for d in dep_list])]

        output_file.write(
            self.module_template.render(docs_title = self.docs_title, module_name=module,
                            is_root_program=is_root_program,
                            file=self.filename_only,
                            sub_list=module_subs,
                            dep_list=dep_list,
                            cls_list=cls_list))

        output_file.flush()
        output_file.close()


    def generateClassDocumentation(self, cls, module, is_root_program):
        procs = self.tparser.class_data[cls]['class_procs']

        # Update proc names
        updated_procs = [ ]
        procs_to_present = [ ]
        for pr in procs:
            sub_full_name = ''

            if isinstance(pr['proc_name'], list) and pr['proc_type'] == 'generic':
                procs_to_present.append(
                    { 'sub_module' : module,
                      'sub_name' : pr['proc_des'],
                      'sub_type' : pr['proc_type'],
                      'sub_mapping' : pr['proc_name'] })

            else:
                #matching = [s for s in self.subs if pr['proc_name'].upper() + '(' in s['sub_name'].upper()]
                matching = [s for s in self.subs if s['sub_name'].upper().startswith(pr['proc_name'].upper() + '(')]

                # Dereference public/private subroutine names
                if len(matching) == 0:
                    sub_full_name = pr['proc_name']
                    updated_procs.append(
                        { 'sub_module' : module,
                          'sub_name' : sub_full_name,
                          'sub_type' : pr['proc_type'],
                          'sub_args' : self.sparser.get_sub_data(pr['proc_name'])['vars'],
                          'sub_comments' : self.sparser.get_sub_data(pr['proc_name'])['comments']} )

                else:
                    sub_full_name = matching[0]
                    updated_procs.append(matching[0])

                    if pr['proc_des'] != None:
                        extracted_arguments = \
                            re.match('([\s\w]+)(?P<arguments>\((.*?)\))', matching[0]['sub_name'], re.IGNORECASE)

                        public_proc_name = pr['proc_des'] + extracted_arguments.group('arguments')

                        if not self.sparser.sub_data.has_key(sub_full_name['sub_name']):
                            print 'Warning, Cannot find a match for: ' + sub_full_name['sub_name']
                        else:
                            procs_to_present.append(
                                { 'sub_module' : module,
                                  'sub_name' : public_proc_name,
                                  'sub_type' : pr['proc_type'],
                                  'sub_args' : self.sparser.get_sub_data(sub_full_name['sub_name'])['vars'],
                                  'sub_comments' : self.sparser.get_sub_data(sub_full_name['sub_name'])['comments']} )

                    else:
                        dic_with_args = matching[0]
                        dic_with_args['sub_type'] = pr['proc_type']
                        dic_with_args['sub_args'] = self.sparser.get_sub_data(sub_full_name['sub_name'])['vars']
                        dic_with_args['sub_comments'] = self.sparser.get_sub_data(sub_full_name['sub_name'])['comments']
                        procs_to_present.append(dic_with_args)

        self.subs_in_classes += updated_procs
        treeForClass = self.tparser.createTreeForType(cls)

        output_file = file(os.path.join(self.output_path, 'class_' + cls.lower() + '.html'), 'w')

        output_file.write(
            self.class_template.render(docs_title = self.docs_title, class_name=cls,
                            is_root_program=is_root_program,
                            module=self.tparser.class_data[cls]['class_in_module'],
                            comment_list=self.tparser.class_data[cls]['class_comments'],
                            file_name=self.filename_only,
                            sub_list=procs_to_present,
                            var_list=self.tparser.class_data[cls]['class_vars'],
                            type_trees=treeForClass))

        output_file.flush()
        output_file.close()
