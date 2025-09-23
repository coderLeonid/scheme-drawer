import json
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Block:
    block_id: str
    block_type: str
    label: str
    condition: str = ""
    next_true: str = ""
    next_false: str = ""
    
    # Координаты и размеры
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    
    # Точки подключения линий
    top_center: Point = None
    bottom_center: Point = None
    left_center: Point = None
    right_center: Point = None

class FlowchartRenderer:
    def __init__(self, json_data):
        self.data = json_data
        self.blocks = {}
        self.connections = []
        
        # Параметры рисования
        self.block_width = 200
        self.block_height = 60
        self.diamond_width = 120
        self.diamond_height = 80
        self.horizontal_spacing = 100
        self.vertical_spacing = 80
        self.margin = 50
        self.connector_radius = 5
        
        # Текущая позиция
        self.current_x = 0
        self.current_y = 0
        
    def calculate_text_dimensions(self, text, max_width=180):
        """Рассчитывает размеры текста и разбивает на строки при необходимости"""
        if not text:
            return [], 80, 40
            
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) * 8 <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
            
        height = len(lines) * 20 + 20
        width = max(len(line) * 8 for line in lines) if lines else 80
        width = min(width + 40, max_width)
        
        return lines, width, height
    
    def create_blocks(self):
        """Создает блоки на основе JSON данных"""
        flowchart = self.data["flowchart"]
        
        for block_id, block_data in flowchart.items():
            block_type = block_data["type"]
            label = block_data.get("label", "")
            condition = block_data.get("condition", "")
            
            block = Block(
                block_id=block_id,
                block_type=block_type,
                label=label,
                condition=condition
            )
            
            # Устанавливаем связи
            if "next" in block_data:
                block.next_true = block_data["next"]
            elif "true" in block_data and "false" in block_data:
                block.next_true = block_data["true"]
                block.next_false = block_data["false"]
                
            self.blocks[block_id] = block
    
    def calculate_positions(self):
        """Рассчитывает позиции всех блоков"""
        # Находим порядок блоков
        order = self._get_blocks_order()
        
        for i, block_id in enumerate(order):
            block = self.blocks[block_id]
            text_lines, text_width, text_height = self.calculate_text_dimensions(block.label)
            
            if block.block_type == "decision":
                block.width = self.diamond_width
                block.height = self.diamond_height
            else:
                block.width = max(text_width, self.block_width)
                block.height = max(text_height, self.block_height)
            
            block.x = self.margin + self.block_width / 2
            block.y = self.margin + i * (self.block_height + self.vertical_spacing)
            
            # Рассчитываем точки подключения
            block.top_center = Point(block.x, block.y)
            block.bottom_center = Point(block.x, block.y + block.height)
            block.left_center = Point(block.x - block.width/2, block.y + block.height/2)
            block.right_center = Point(block.x + block.width/2, block.y + block.height/2)
    
    def _get_blocks_order(self):
        """Возвращает порядок блоков в правильной последовательности"""
        order = []
        current = "start"
        visited = set()
        
        while current and current not in visited:
            visited.add(current)
            order.append(current)
            
            block = self.blocks[current]
            if block.next_true and block.next_true not in visited:
                current = block.next_true
            else:
                break
                
        # Добавляем оставшиеся блокы
        for block_id in self.blocks:
            if block_id not in visited:
                order.append(block_id)
                
        return order
    
    def generate_svg(self):
        """Генерирует SVG код блок-схемы"""
        self.create_blocks()
        self.calculate_positions()
        
        # Рассчитываем общие размеры
        max_y = max(block.y + block.height for block in self.blocks.values()) + self.margin
        max_x = max(block.x + block.width/2 for block in self.blocks.values()) + self.margin * 2
        
        svg = f'''<svg width="{int(max_x)}" height="{int(max_y)}" xmlns="http://www.w3.org/2000/svg">
<style>
    .block {{ fill: white; stroke: black; stroke-width: 2; }}
    .decision {{ fill: #e6f3ff; stroke: #0066cc; }}
    .startend {{ fill: #f0f0f0; stroke: #333; }}
    .text {{ font-family: Arial, sans-serif; font-size: 12px; fill: #333; }}
    .line {{ stroke: black; stroke-width: 2; fill: none; }}
</style>
<defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
    </marker>
</defs>
'''
        
        # Рисуем линии соединений
        svg += self._draw_connections()
        
        # Рисуем блоки
        for block in self.blocks.values():
            svg += self._draw_block(block)
        
        svg += '</svg>'
        return svg
    
    def _draw_block(self, block):
        """Рисует отдельный блок"""
        if block.block_type == "start" or block.block_type == "end":
            return self._draw_ellipse(block)
        elif block.block_type == "decision":
            return self._draw_diamond(block)
        else:
            return self._draw_rectangle(block)
    
    def _draw_rectangle(self, block):
        """Рисует прямоугольный блок"""
        x = block.x - block.width/2
        y = block.y
        text_lines, _, _ = self.calculate_text_dimensions(block.label)
        
        svg = f'<rect x="{x:.1f}" y="{y:.1f}" width="{block.width:.1f}" height="{block.height:.1f}" class="block"/>\n'
        
        # Текст
        text_y = y + 20
        for i, line in enumerate(text_lines):
            # Экранируем специальные символы XML
            line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            svg += f'<text x="{block.x:.1f}" y="{text_y + i*15:.1f}" text-anchor="middle" class="text">{line_escaped}</text>\n'
        
        return svg
    
    def _draw_ellipse(self, block):
        """Рисует эллиптический блок (начало/конец)"""
        rx = block.width / 2
        ry = block.height / 3
        svg = f'<ellipse cx="{block.x:.1f}" cy="{block.y + ry:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" class="block startend"/>\n'
        
        # Текст
        text_lines, _, _ = self.calculate_text_dimensions(block.label)
        text_y = block.y + ry
        for i, line in enumerate(text_lines):
            line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            svg += f'<text x="{block.x:.1f}" y="{text_y + i*15:.1f}" text-anchor="middle" class="text">{line_escaped}</text>\n'
        
        return svg
    
    def _draw_diamond(self, block):
        """Рисует ромб (условие)"""
        points = [
            f"{block.x:.1f},{block.y:.1f}",
            f"{block.x + block.width/2:.1f},{block.y + block.height/2:.1f}",
            f"{block.x:.1f},{block.y + block.height:.1f}",
            f"{block.x - block.width/2:.1f},{block.y + block.height/2:.1f}"
        ]
        points_str = " ".join(points)
        svg = f'<polygon points="{points_str}" class="block decision"/>\n'
        
        # Текст условия
        if block.condition:
            text_lines, _, _ = self.calculate_text_dimensions(block.condition)
            text_y = block.y + block.height/2 - (len(text_lines)-1)*7.5
            for i, line in enumerate(text_lines):
                line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                svg += f'<text x="{block.x:.1f}" y="{text_y + i*15:.1f}" text-anchor="middle" class="text">{line_escaped}</text>\n'
        
        return svg
    
    def _draw_connections(self):
        """Рисует линии соединений между блоками"""
        svg = ""
        
        for block in self.blocks.values():
            if block.next_true:
                next_block = self.blocks.get(block.next_true)
                if next_block:
                    svg += self._draw_connection(block, next_block, True)
            
            if block.next_false:
                next_block = self.blocks.get(block.next_false)
                if next_block:
                    svg += self._draw_connection(block, next_block, False)
        
        return svg
    
    def _draw_connection(self, from_block, to_block, is_true_branch):
        """Рисует линию соединения между двумя блоками"""
        if from_block.block_type == "decision":
            if is_true_branch:
                # Из нижней точки ромба
                start_x, start_y = from_block.bottom_center.x, from_block.bottom_center.y
            else:
                # Из правой точки ромба
                start_x, start_y = from_block.right_center.x, from_block.right_center.y
        else:
            # Из нижней точки прямоугольника
            start_x, start_y = from_block.bottom_center.x, from_block.bottom_center.y
        
        # В верхнюю точку следующего блока
        end_x, end_y = to_block.top_center.x, to_block.top_center.y
        
        # Промежуточная точка для плавного изгиба
        mid_y = (start_y + end_y) / 2
        
        path = f"M {start_x:.1f} {start_y:.1f} " \
               f"L {start_x:.1f} {mid_y:.1f} " \
               f"L {end_x:.1f} {mid_y:.1f} " \
               f"L {end_x:.1f} {end_y:.1f}"
        
        return f'<path d="{path}" class="line" marker-end="url(#arrowhead)"/>\n'

def create_sample_flowchart():
    """Создает пример блок-схемы для тестирования"""
    json_data = {
        "function": {
            "name": "selectionSort",
            "parameters": [
                {"name": "row", "type": "RowType", "reference": True},
                {"name": "start", "type": "int"},
                {"name": "end", "type": "int"},
                {"name": "reverse", "type": "bool"}
            ],
            "returnType": "void"
        },
        "flowchart": {
            "start": {
                "type": "start",
                "label": "Начало selectionSort",
                "next": "sort_loop_init"
            },
            "sort_loop_init": {
                "type": "operation",
                "label": "i = end",
                "next": "sort_loop_condition"
            },
            "sort_loop_condition": {
                "type": "decision",
                "condition": "i > start",
                "true": "find_max_init",
                "false": "reverse_check"
            },
            "find_max_init": {
                "type": "operation",
                "label": "maxIndex = start, j = start + 1",
                "next": "find_max_condition"
            },
            "find_max_condition": {
                "type": "decision",
                "condition": "j <= i",
                "true": "compare_elements",
                "false": "swap_elements"
            },
            "compare_elements": {
                "type": "decision",
                "condition": "row[j] > row[maxIndex]",
                "true": "update_max",
                "false": "increment_j"
            },
            "update_max": {
                "type": "operation",
                "label": "maxIndex = j",
                "next": "increment_j"
            },
            "increment_j": {
                "type": "operation",
                "label": "j++",
                "next": "find_max_condition"
            },
            "swap_elements": {
                "type": "operation",
                "label": "swap elements and i--",
                "next": "sort_loop_condition"
            },
            "reverse_check": {
                "type": "decision",
                "condition": "reverse == true",
                "true": "reverse_init",
                "false": "end"
            },
            "reverse_init": {
                "type": "operation",
                "label": "i = start, j = end",
                "next": "reverse_condition"
            },
            "reverse_condition": {
                "type": "decision",
                "condition": "i < j",
                "true": "reverse_swap",
                "false": "end"
            },
            "reverse_swap": {
                "type": "operation",
                "label": "swap and increment/decrement",
                "next": "reverse_condition"
            },
            "end": {
                "type": "end",
                "label": "Конец selectionSort"
            }
        }
    }
    return json_data

def main():
    # Создаем пример данных
    json_data = create_sample_flowchart()
    
    # Создаем рендерер и генерируем SVG
    renderer = FlowchartRenderer(json_data)
    svg_content = renderer.generate_svg()
    
    # Сохраняем в файл
    with open("flowchart.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print("Блок-схема сохранена в файл flowchart.svg")
    
    # Также создаем HTML для просмотра
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Блок-схема selectionSort</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Блок-схема функции selectionSort</h1>
        {svg_content}
    </div>
</body>
</html>
'''
    
    with open("flowchart.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("HTML версия сохранена в файл flowchart.html")

if __name__ == "__main__":
    main()
