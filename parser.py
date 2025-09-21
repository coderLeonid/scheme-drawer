import re
import pygame

with open("output.txt", "w", encoding="utf-8"):
    pass
with open("file.txt", "r", encoding="utf-8") as f:
    lines = [line.strip('\n') for line in f]

endline = lines[-1]
func_mother = re.match('([a-z0-9_]+)( [a-z0-9_]+)+', endline)[0].split() if re.match('([a-z0-9_]+)( [a-z0-9_]+)+', endline) else ['what?']

save_pointer = False
if re.search(r'PTR$', endline):
    save_pointer = True
lines = '\n'.join(lines)
lines = re.sub(r'(?s)\s*/\*.*?\*/', '', lines)
lines = lines.split('\n')
lines = [re.sub(r'\s*//.*', '', i) for i in lines]

lines = [(i[:-1] if i[-1:] == ';' else i).rstrip() for i in lines]
types = '(?:int|double|float|bool|string|void|const)'
if 'typedef' in '\n'.join(lines):
    types = f'(?:int|double|float|bool|string|void|const|{'|'.join([re.sub(r'\[.*\]', '', i.split()[-1]) for i in lines if re.match('typedef', i)])})'
type_links = f'{types}{'(?: (\*|&)+| |(\*|&)+ )' if not save_pointer else ' ?'}'

lines = [re.sub(fr'^\s*{type_links}\w+(?:, (?:{type_links})?\w+)*$', '', i) for i in lines]
lines = [re.sub(fr'(?<!typedef ){type_links}', '', i) for i in lines]

if save_pointer:
    lines = [re.sub(r', (\*|&) (\w+)', r', \1\2', i) for i in lines]

lines = [i for i in lines if not re.fullmatch(r'\s*', i)]
lines = [i for indx, i in enumerate(lines[:-1]) if not (re.match(r'[а-яА-Я]|#include|using|typedef|\s*setlocale|\w+\(.+\)(?!\{)', i)) or re.match(r'\s*\{', lines[indx + 1])] # clearing first strings of code
lines = [re.sub('} while', 'while', i) for i in lines]

lines = [re.sub(r'((?:for|if|while|switch|case) )\((.*)\)', r'\1\2', re.sub(r'(.*)\{|\}(.*)', r'\1', i)) for i in lines]
lines = [re.sub(r'f?abs\((.*?)\)', r'|\1|', re.sub(r'sqrt\((-?\d+(\.\d+)?)\)', r'√\1', i).replace('sqrt', '√')) for i in lines]
lines = [re.sub(r'(\D)\.(\d)', r'\g<1>0.\2', re.sub(r'(\d)\.(\D|$)', r'\1\2', i)) for i in lines]
for indx in range(len(lines)):
    while re.search(r'(\w+|\)|\|) ([\/\*\+\-=<>]=?|(?:&&|\|\|)) (\w+|\(|\||√)', lines[indx]):
        lines[indx] = re.sub(r'(\w+|\)|\|) ([\/\*\+\-=<>]=?|(?:&&|\|\|)) (\w+|\(|\||√)', r'\1\2\3', lines[indx])
        
lines = [re.sub(r'(?<=\W)(\d+)\*([a-zA-Z](?!\d)|√|\()', r'\1\2', i) for i in lines]
lines = [re.sub(r'(\))\*(\()', r'\1\2', i) for i in lines]

for j in range(10, 0, -1):
    copyed_muls = {indx:re.search(fr'([a-zA-Z]\w*)(?:\*\1){{{j},}}', i) for indx, i in enumerate(lines) if re.search(fr'([a-zA-Z]\w*)(?:\*\1){{{j},}}', i)}
    vars_to_pow = {indx:re.match(r'[a-zA-Z]\w*', i[0]) for indx, i in copyed_muls.items()}
    pow_powers = {indx: f'{vars_to_pow[indx][0]}^{len(i[0].split('*'))}' for indx, i in copyed_muls.items()}

    for indx in pow_powers:
        lines[indx] = lines[indx].replace(copyed_muls[indx][0], pow_powers[indx])

for indx, i in enumerate(lines):
    a = re.search(r'(\w+|\(.*\))(\*\1)*', i)
    if a:
        a = a[0]
        serch = re.match(r'\w+', a)[0]
        i = re.sub(a, f'{serch}^{len(re.findall(serch, a))}', i)
        
lines = [re.sub(r' {4}', ' ', i) for i in lines if not re.fullmatch('\W*', i)]

for indx, i in enumerate(lines):
    a = re.match(r'\s*', i)[0]
    lines[indx] = re.sub(r'^\s*', str(len(a)), i)

for indx in range(len(lines)):
    while lines[indx].count('*(') > len(re.findall(r'[^ \(]\*\(', lines[indx])):
        lines[indx] = re.sub(r'(?<!\*)\(([^\(\)]*?)\)', r'OPENscope\1CLOSEscope', lines[indx])
        lines[indx] = re.sub(r'\*\((\w+(?:\[.+?\])*)\+(.+?)\)', r'\1\[\2\]', lines[indx])
        lines[indx] = lines[indx].replace('\[', '[').replace('\]', ']')
        lines[indx] = lines[indx].replace('OPENscope', '(').replace('CLOSEscope', ')')
        

lines = [re.sub(r'(?:, \w+)+$', '', i) for i in lines]
lines_joined = '\n'.join(lines[:-1])

lines = [re.sub('(\d)(?:\w+, )+', r'\1', i).rstrip() for i in lines]

for func in func_mother:
    if func in lines_joined:
        lines_old = lines[:]
        lines = []
        break
for func in func_mother:
    if func not in lines_joined:
        continue
    indx_start, indx_end = [], []
    for indx1, i1 in enumerate(lines_old[:-1]):
        if not re.match(f'0(?:{types} )?{func}', i1):
            continue
        indx_start.append(indx1)
        for indx2, i2 in enumerate(lines_old[indx_start[-1] + 1:-1]):
            if i2[:1] == '0':
                indx_end.append(indx_start[-1] + 1 + indx2)
                break
        else:
            indx_end.append('end')

    lines_new = []
    for i in range(len(indx_start)):
        if indx_end[i] != 'end':
            lines_new.extend(lines_old[indx_start[i]:indx_end[i]])
        else:
            lines_new.extend(lines_old[indx_start[i]:])
    lines += lines_new
            

for i in lines:
    print(i)

with open("output.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")