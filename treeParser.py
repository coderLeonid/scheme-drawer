import json
from tree_sitter import Language, Parser
import tree_sitter_cpp

CPP_LANGUAGE = Language(tree_sitter_cpp.language())
parser = Parser(CPP_LANGUAGE)

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return bytes(file.read(), "utf8")

def extract_flow_elements(node, code_bytes, parent_type=None):
    """Извлекает элементы, важные для построения блок-схемы"""
    elements = []
    
    # Основные структурные элементы
    flow_nodes = [
        'function_definition',    # Функции
        'if_statement',           # Условия if
        'for_statement',          # Циклы for
        'while_statement',        # Циклы while
        'do_statement',           # Циклы do-while
        'switch_statement',       # Switch
        'case_statement',         # Case в switch
        'return_statement',       # Return
        'break_statement',        # Break
        'continue_statement',     # Continue
        'compound_statement',     # Блоки кода { }
        'expression_statement',   # Выражения (вызовы функций и т.д.)
    ]
    
    if node.type in flow_nodes:
        element_info = {
            'type': node.type,
            'text': code_bytes[node.start_byte:node.end_byte].decode('utf8', errors='ignore').strip(),
            'start_line': node.start_point[0] + 1,  # +1 для человекочитаемых номеров строк
            'end_line': node.end_point[0] + 1,
            'start_column': node.start_point[1],
            'end_column': node.end_point[1],
            'children': []
        }
        
        # Добавляем специфичную информацию для разных типов элементов
        if node.type == 'function_definition':
            element_info['name'] = extract_function_name(node, code_bytes)
            element_info['return_type'] = extract_return_type(node, code_bytes)
        
        elif node.type == 'if_statement':
            element_info['condition'] = extract_condition(node, code_bytes)
            element_info['has_else'] = has_else_branch(node)
        
        elif node.type in ['for_statement', 'while_statement']:
            element_info['condition'] = extract_loop_condition(node, code_bytes)
        
        elif node.type == 'switch_statement':
            element_info['expression'] = extract_switch_expression(node, code_bytes)
        
        elements.append(element_info)
        parent_type = node.type
    
    # Рекурсивно обходим детей
    for child in node.children:
        child_elements = extract_flow_elements(child, code_bytes, parent_type)
        if child_elements:
            if elements and 'children' in elements[-1]:
                elements[-1]['children'].extend(child_elements)
            else:
                elements.extend(child_elements)
    
    return elements

def extract_function_name(node, code_bytes):
    """Извлекает имя функции"""
    for child in node.children:
        if child.type == 'function_declarator':
            for subchild in child.children:
                if subchild.type == 'identifier':
                    return code_bytes[subchild.start_byte:subchild.end_byte].decode('utf8')
    return "anonymous"

def extract_return_type(node, code_bytes):
    """Извлекает тип возвращаемого значения"""
    for child in node.children:
        if child.type in ['primitive_type', 'type_identifier']:
            return code_bytes[child.start_byte:child.end_byte].decode('utf8')
    return "void"

def extract_condition(node, code_bytes):
    """Извлекает условие if statement"""
    for child in node.children:
        if child.type == 'condition':
            return code_bytes[child.start_byte:child.end_byte].decode('utf8', errors='ignore').strip()
    return ""

def extract_loop_condition(node, code_bytes):
    """Извлекает условие цикла"""
    for child in node.children:
        if child.type == 'condition':
            return code_bytes[child.start_byte:child.end_byte].decode('utf8', errors='ignore').strip()
    return ""

def extract_switch_expression(node, code_bytes):
    """Извлекает выражение switch"""
    for child in node.children:
        if child.type == 'condition':
            return code_bytes[child.start_byte:child.end_byte].decode('utf8', errors='ignore').strip()
    return ""

def has_else_branch(node):
    """Проверяет наличие else ветки"""
    for child in node.children:
        if child.type == 'else':
            return True
    return False

# Основной код
code_bytes = read_file('data/test.cpp')
tree = parser.parse(code_bytes)

# Извлекаем элементы для блок-схемы
flow_elements = extract_flow_elements(tree.root_node, code_bytes)

# Создаем структурированный результат
flow_data = {
    'filename': 'test.cpp',
    'functions': [],
    'control_structures': []
}

# Разделяем на функции и контрольные структуры
for element in flow_elements:
    if element['type'] == 'function_definition':
        flow_data['functions'].append(element)
    else:
        flow_data['control_structures'].append(element)

# Сохраняем в JSON
with open('flow_data.json', 'w', encoding='utf-8') as f:
    json.dump(flow_data, f, indent=2, ensure_ascii=False)

print(f"Извлечено {len(flow_data['functions'])} функций и {len(flow_data['control_structures'])} контрольных структур")
print("Данные для блок-схемы сохранены в flow_data.json")
