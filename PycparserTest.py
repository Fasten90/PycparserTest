
import pycparser

"""
preprocess_file
parse_file
"""

#test_file_path = r"test\test.c"
test_file_path = r"../../AtollicWorkspace/FastenHomeAut/Src/Common/Helper/StringHelper.c"

preprocessor_path = r"gcc"
#preprocessor_args = "-E"
# now, pycparser git repository has been downloaded into this directory (pycparser dir)
preprocessor_args = ["-E", r"-Ipycparser/utils/fake_libc_include"]
# Added because FastenHome
preprocessor_args.append("-I../../AtollicWorkspace/FastenHomeAut/Inc/Common")
preprocessor_args.append("-I../../AtollicWorkspace/FastenHomeAut/Inc/Common/Helper")
preprocessor_args.append("-I../../AtollicWorkspace/FastenHomeAut/Inc")
preprocessor_args.append("-I../../AtollicWorkspace/FastenHomeAut/Drivers/x86/Inc")
preprocessor_args.append("-DCONFIG_PLATFORM_X86")
preprocessor_args.append("-DCONFIG_USE_PANEL_PC")
# Could be use [] (list)

preprocessed_file_path = r"test\test_preprocessed.c"

pycparser_ast_generated = r"test\ast_generated.txt"

preprocessed_file_content = pycparser.preprocess_file(test_file_path, cpp_path=preprocessor_path, cpp_args=preprocessor_args)

with open(preprocessed_file_path, "w") as f:
    f.write(preprocessed_file_content)

# This only want preprocessed file!
parse_result = pycparser.parse_file(preprocessed_file_path)
# use_cpp=False, cpp_path='cpp', cpp_args='',
#                parser=None
# TODO: Test this: use_cpp=True - only for preprocessor

parse_result_str = str(parse_result)
print(parse_result_str)

print("##########################")

for ast_item in parse_result:
    print(str(ast_item))

print("##########################")

parse_result.show()


func_declarations = set()
func_calls = set()


# Note: be careful, this was child of a pycparser class
class FuncCallVisitor(pycparser.c_ast.NodeVisitor):

    def __init__(self):
        pass

    # Note: https://github.com/eliben/pycparser/blob/master/examples/func_calls.py
    def visit_FuncCall(self, node):
        # This was called by pycparser NodeVisitor automatically
        if node.name.name == "my_test_func" or node.name.name == "printf":
            print("Called '{}' at '{}'".format(node.name.name, node.name.coord))
        else:
            print("Called another, unknown function: '{}' from '{}'".format(node.name.name, node.name.coord))

        global func_calls
        func_calls.add(node.name.name)
        # Visit args in case they contain more func calls.
        if node.args:
            print("Called an another function from: '{}'".format(node.name.name))
            self.visit(node.args)  # Recursion


class FuncDefVisitor(pycparser.c_ast.NodeVisitor):
    # Note: https://github.com/eliben/pycparser/blob/master/examples/func_defs.py
    def visit_FuncDef(self, node):
        # This was called by pycparser NodeVisitor automatically
        print("'{}' at '{}' %".format(node.decl.name, node.decl.coord))

        global func_declarations
        func_declarations.add(node.decl.name)


checker_obj = FuncCallVisitor()
checker_obj.visit(parse_result)
checker_obj = FuncDefVisitor()
checker_obj.visit(parse_result)


# Listing
func_calls_str = "".join(item + "\n" for item in func_calls)
func_def_str = "".join(item + "\n" for item in func_declarations)

print("######################")
print("Func definitions:")
print(func_def_str)

print("######################")
print("Func calls:")
print(func_calls_str)

# Not used functions:
print("######################")
print("Not used functions:")
func_not_used = func_declarations - func_calls
func_not_used_str = "".join(item + "\n" for item in func_not_used)
print(func_not_used_str)


# Save the AST to file
with open(pycparser_ast_generated, "w") as f:
    f.write(parse_result_str)


