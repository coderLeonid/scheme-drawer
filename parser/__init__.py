from parser import *

if __name__ == 'main':
    import json
    from parser.parser import parserCPP

    file_path = '../data/test.cpp'
    with open(file_path, 'r', encoding='utf-8') as file:
        bytes_file = bytes(file.read(), 'utf8')

    data = parserCPP(bytes_file)

    with open('../output/output_cpp.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
