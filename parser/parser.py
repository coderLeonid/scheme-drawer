from tree_sitter import Language, Parser

import tree_sitter_cpp


CPP_LANGUAGE = Language(tree_sitter_cpp.language())
parser_cpp = Parser(CPP_LANGUAGE)


def parserCPP(bytes):
    return tree_to_json(parser_cpp.parse(bytes).root_node)


def tree_to_json(node):
    result = {
        'type': node.type,
        'text': node.text.decode('utf8') if node.child_count == 0 else None,
    }
    
    children = []
    for child in node.children:
        children.append(tree_to_json(child))
    
    if children:
        result['children'] = children
    
    return result
