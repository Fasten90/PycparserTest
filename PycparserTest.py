
import pycparser

"""
preprocess_file
parse_file
"""

#test_file_path = r"test\test.c"
#test_file_path = r"../../AtollicWorkspace/FastenHomeAut/Src/Common/Helper/StringHelper.c"
test_file_path = r"../../AtollicWorkspace/FastenHomeAut/Src/Common/Helper/MathHelper.c"

preprocessor_path = r"gcc"
#preprocessor_args = "-E"
# now, pycparser git repository has been downloaded into this directory (pycparser dir)
preprocessor_args = ["-E", r"-Ipycparser/utils/fake_libc_include"]

# TODO: Add them to list
# TODO: Read from file
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

# Save the AST to file
with open(pycparser_ast_generated, "w") as f:
    f.write(parse_result_str)


# Print AST
#print("##########################")
#for ast_item in parse_result:
#    print(str(ast_item))

# TODO: Print AST
#print("##########################")
#parse_result.show()


func_declarations = set()
func_calls = set()
goto_used = set()
return_used = set()
func_calls_all = []

# Note: be careful, this was child of a pycparser class
class FuncCallVisitor(pycparser.c_ast.NodeVisitor):

    def __init__(self):
        pass

    # Note: https://github.com/eliben/pycparser/blob/master/examples/func_calls.py
    def visit_FuncCall(self, node):
        # This was called by pycparser NodeVisitor automatically
        # TODO: Dont care which function
        if node.name.name == "my_test_func" or node.name.name == "printf":
            print("Called '{}' at '{}'".format(node.name.name, node.name.coord))
        else:
            print("Called '{}' function from '{}'".format(node.name.name, node.name.coord))

        global func_calls
        global func_calls_all
        func_calls.add(node.name.name)
        func_calls_all.append((node.name.name, node.name.coord))
        # Visit args in case they contain more func calls.
        if node.args:
            print("Called an another function from: '{}'".format(node.name.name))
            self.visit(node.args)  # Recursion


class FuncDefVisitor(pycparser.c_ast.NodeVisitor):
    # Note: https://github.com/eliben/pycparser/blob/master/examples/func_defs.py
    def visit_FuncDef(self, node):
        # This was called by pycparser NodeVisitor automatically
        print("Function declaration: '{}' at '{}'".format(node.decl.name, node.decl.coord))

        global func_declarations
        func_declarations.add(node.decl.name)


# Goto checker
class GotoVisitor(pycparser.c_ast.NodeVisitor):
    # Note: https://github.com/eliben/pycparser/blob/master/examples/func_defs.py
    def visit_Goto(self, node):
        # This was called by pycparser NodeVisitor automatically
        print("Goto used '{}' at '{}'".format(node.name, node.coord))

        global goto_used
        goto_used.add(node.name)


# Return checker
class ReturnVisitor(pycparser.c_ast.NodeVisitor):
    def visit_Return(self, node):
        # This was called by pycparser NodeVisitor automatically
        #print("Return used '{}' at '{}'".format(node.name, node.coord))

        global return_used
        return_used.add(node.coord)


checker_obj = FuncCallVisitor()
checker_obj.visit(parse_result)

checker_obj = FuncDefVisitor()
checker_obj.visit(parse_result)

# Goto
checker_obj = GotoVisitor()
checker_obj.visit(parse_result)

# Return
# TODO: Cannot check easily, which function' return
checker_obj = ReturnVisitor()
checker_obj.visit(parse_result)


def find_return_in_recursive(item_list):
    return_count = 0
    if isinstance(item_list, pycparser.c_ast.Return):
        return 1
    for item in item_list:
        return_count += find_return_in_recursive(item)
    return return_count



# Explore AST
for ast_item in parse_result:
    #print(str(ast_item))
    #if isinstance(ast_item, list):  # pycparser.c_ast.FuncDecl
    #if ast_item.storage[0] != "typedef":
    #if isinstance(ast_item.type, pycparser.c_ast.FuncDecl):
    #if isinstance(ast_item.type, pycparser.c_ast.FuncDef):
    if isinstance(ast_item, pycparser.c_ast.FuncDef):
        # Explorer the body
        function_name = ast_item.decl.name
        return_count = 0
        for body_item in ast_item.body:
            #print(str(body_item))
            #if isinstance(body_item, pycparser.c_ast.Return):
            #    return_count += 1
            return_count = find_return_in_recursive(body_item)
        print("Function: '{}' has {} return".format(function_name, return_count))


# Listing
func_calls_str = "".join(item + "\n" for item in func_calls)
func_def_str = "".join(item + "\n" for item in func_declarations)

print("######################")
print("Func definitions: (Declared functions)")
print(func_def_str)

print("######################")
print("Func calls: (Called functions)")
print(func_calls_str)

# Not used functions:
print("######################")
print("Not used functions:")
func_not_used = func_declarations - func_calls
func_not_used_str = "".join(item + "\n" for item in func_not_used)
print(func_not_used_str)

goto_used_str = "".join(item + "\n" for item in goto_used)
print("######################")
print("Goto used:")
print(goto_used_str)


# Try collect, an function where was called
func_call_all_list = {}
for an_func_call in func_calls_all:
    # Check keyword
    an_func_call[0]
    if an_func_call[0] in func_call_all_list:
        # If is in, add this called function
        func_call_all_list[an_func_call[0]].append(an_func_call[1])
    else:
        # Not in, new
        func_call_all_list[an_func_call[0]] = [an_func_call[1]]

print("######################")
print("Calls")
# ugly format
#print(func_call_all_list)
#for item in func_call_all_list.items():
for key, value in func_call_all_list.items():
    print("'{}' called from:\n"
          "{}".format(
                key,
                "".join(["  " + item.file + ":" + str(item.line) + "\n" for item in value])))

