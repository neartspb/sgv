# общий скрипт для всех элементов
import tkinter as tk
from tkinter import filedialog
import re
import math
import xml.etree.ElementTree as ET

# Функция для парсинга трансформаций (translate, rotate, scale)
def parse_transform(transform):
    translate = [0, 0]
    rotate = 0
    scale = [1, 1]

    translate_match = re.search(r'translate\(([^)]+)\)', transform)
    if translate_match:
        translate = list(map(float, re.split(r'[ ,]+', translate_match.group(1))))

    rotate_match = re.search(r'rotate\(([^)]+)\)', transform)
    if rotate_match:
        rotate = float(rotate_match.group(1))

    scale_match = re.search(r'scale\(([^)]+)\)', transform)
    if scale_match:
        scale = list(map(float, re.split(r'[ ,]+', scale_match.group(1))))
        if len(scale) == 1:
            scale.append(scale[0])

    return translate, rotate, scale

# Функция для трансформации точки с учетом translate, rotate и scale
def transform_point(x, y, translate, rotate, scale):
    x *= scale[0]
    y *= scale[1]

    rad_rotate = math.radians(rotate)
    x_rot = x * math.cos(rad_rotate) - y * math.sin(rad_rotate)
    y_rot = x * math.sin(rad_rotate) + y * math.cos(rad_rotate)

    x_trans = x_rot + translate[0]
    y_trans = y_rot + translate[1]

    return x_trans, y_trans
# Функция для преобразования эллипса в полигон
def ellipse_to_polygon(cx, cy, rx, ry, transform, num_points=100):
    translate, rotate, scale = parse_transform(transform)
    points = []

    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = rx * math.cos(angle)
        y = ry * math.sin(angle)
        x_trans, y_trans = transform_point(x, y, translate, rotate, scale)
        points.append((cx + x_trans, cy + y_trans))

    return points

# Функция для преобразования полигона в path
def polygon_to_path(points, fill, fill_opacity, elem_id):
    d = "M " + " L ".join([f"{x},{y}" for x, y in points]) + " Z"
    return {
        'id': elem_id,
        'd': d,
        'stroke': fill,
        'stroke-opacity': fill_opacity,
        'stroke-width': '1',
        'fill': 'none'
    }

# Функция для преобразования прямоугольника в path
def rect_to_path(x, y, width, height, fill, fill_opacity, elem_id):
    d = f'M {x},{y} h {width} v {height} h {-width} Z'
    return {
        'id': elem_id,
        'd': d,
        'stroke': fill,
        'stroke-opacity': fill_opacity,
        'stroke-width': '1',
        'fill': 'none'
    }

# Функция для преобразования круга в path
def circle_to_path(cx, cy, r, fill, fill_opacity, elem_id):
    d = f'M {cx - r},{cy} a {r},{r} 0 1,0 {2 * r},0 a {r},{r} 0 1,0 {-2 * r},0'
    return {
        'id': elem_id,
        'd': d,
        'stroke': fill,
        'stroke-opacity': fill_opacity,
        'stroke-width': '1',
        'fill': 'none'
    }

# Функция для преобразования линии в path
def line_to_path(x1, y1, x2, y2, stroke, stroke_width, stroke_opacity, elem_id):
    d = f'M {x1},{y1} L {x2},{y2}'
    return {
        'id': elem_id,
        'd': d,
        'stroke': stroke,
        'stroke-opacity': stroke_opacity,
        'stroke-width': stroke_width,
        'fill': 'none'
    }

# Функция для преобразования полилинии в path
def polyline_to_path(points, stroke, stroke_width, stroke_opacity, elem_id):
    d = "M " + " L ".join(points)
    return {
        'id': elem_id,
        'd': d,
        'stroke': stroke,
        'stroke-opacity': stroke_opacity,
        'stroke-width': stroke_width,
        'fill': 'none'
    }

# Функция для преобразования полигона в path
def polygon_to_path(points, fill, fill_opacity, elem_id):
    d = "M " + " L ".join(points) + " Z"
    return {
        'id': elem_id,
        'd': d,
        'stroke': fill,
        'stroke-opacity': fill_opacity,
        'stroke-width': '1',
        'fill': 'none'
    }
# Функция для обработки и преобразования SVG файла
def convert_svg(file_path, output_paths):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for element in root.iter():
        if element.tag == 'circle':
            cx = float(element.get('cx'))
            cy = float(element.get('cy'))
            r = float(element.get('r'))
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            path = circle_to_path(cx, cy, r, fill, fill_opacity, elem_id)
            output_paths['circle'].append(path)
        elif element.tag == 'ellipse':
            cx = float(element.get('cx'))
            cy = float(element.get('cy'))
            rx = float(element.get('rx'))
            ry = float(element.get('ry'))
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            transform = element.get('transform', '')
            points = ellipse_to_polygon(cx, cy, rx, ry, transform)
            path = polygon_to_path(points, fill, fill_opacity, elem_id)
            output_paths['ellipse'].append(path)
        elif element.tag == 'line':
            x1 = float(element.get('x1'))
            y1 = float(element.get('y1'))
            x2 = float(element.get('x2'))
            y2 = float(element.get('y2'))
            stroke = element.get('stroke')
            stroke_width = element.get('stroke-width')
            stroke_opacity = element.get('stroke-opacity')
            elem_id = element.get('id')
            path = line_to_path(x1, y1, x2, y2, stroke, stroke_width, stroke_opacity, elem_id)
            output_paths['line'].append(path)
        elif element.tag == 'polyline':
            points = element.get('points').split()
            stroke = element.get('stroke')
            stroke_width = element.get('stroke-width')
            stroke_opacity = element.get('stroke-opacity')
            elem_id = element.get('id')
            path = polyline_to_path(points, stroke, stroke_width, stroke_opacity, elem_id)
            output_paths['polyline'].append(path)
        elif element.tag == 'polygon':
            points = element.get('points').split()
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            path = polygon_to_path(points, fill, fill_opacity, elem_id)
            output_paths['polygon'].append(path)
        elif element.tag == 'rect':
            x = float(element.get('x'))
            y = float(element.get('y'))
            width = float(element.get('width'))
            height = float(element.get('height'))
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            path = rect_to_path(x, y, width, height, fill, fill_opacity, elem_id)
            output_paths['rect'].append(path)

# Функция для выбора файла и запуска конвертации
def choose_file():
    root.update()  # Ensure dialog opens on top
    file_path = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
    if file_path:
        output_paths = {
            'circle': [],
            'ellipse': [],
            'line': [],
            'polyline': [],
            'polygon': [],
            'rect': []
        }
        convert_svg(file_path, output_paths)
        for key, paths in output_paths.items():
            if paths:
                output_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")], initialfile=f"{key}.svg")
                if output_path:
                    with open(output_path, 'w') as file:
                        file.write('<?xml version="1.0" standalone="no"?>\n')
# Функция для обработки и преобразования SVG файла
def convert_svg(file_path, output_paths):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for element in root.iter():
        if element.tag == 'circle':
            cx = float(element.get('cx'))
            cy = float(element.get('cy'))
            r = float(element.get('r'))
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            path = circle_to_path(cx, cy, r, fill, fill_opacity, elem_id)
            output_paths['circle'].append(path)
        elif element.tag == 'ellipse':
            cx = float(element.get('cx'))
            cy = float(element.get('cy'))
            rx = float(element.get('rx'))
            ry = float(element.get('ry'))
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            transform = element.get('transform', '')
            points = ellipse_to_polygon(cx, cy, rx, ry, transform)
            path = polygon_to_path(points, fill, fill_opacity, elem_id)
            output_paths['ellipse'].append(path)
        elif element.tag == 'line':
            x1 = float(element.get('x1'))
            y1 = float(element.get('y1'))
            x2 = float(element.get('x2'))
            y2 = float(element.get('y2'))
            stroke = element.get('stroke')
            stroke_width = element.get('stroke-width')
            stroke_opacity = element.get('stroke-opacity')
            elem_id = element.get('id')
            path = line_to_path(x1, y1, x2, y2, stroke, stroke_width, stroke_opacity, elem_id)
            output_paths['line'].append(path)
        elif element.tag == 'polyline':
            points = element.get('points').split()
            stroke = element.get('stroke')
            stroke_width = element.get('stroke-width')
            stroke_opacity = element.get('stroke-opacity')
            elem_id = element.get('id')
            path = polyline_to_path(points, stroke, stroke_width, stroke_opacity, elem_id)
            output_paths['polyline'].append(path)
        elif element.tag == 'polygon':
            points = element.get('points').split()
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            path = polygon_to_path(points, fill, fill_opacity, elem_id)
            output_paths['polygon'].append(path)
        elif element.tag == 'rect':
            x = float(element.get('x'))
            y = float(element.get('y'))
            width = float(element.get('width'))
            height = float(element.get('height'))
            fill = element.get('fill')
            fill_opacity = element.get('fill-opacity')
            elem_id = element.get('id')
            path = rect_to_path(x, y, width, height, fill, fill_opacity, elem_id)
            output_paths['rect'].append(path)

# Функция для выбора файла и запуска конвертации
def choose_file():
    root.update()  # Ensure dialog opens on top
    file_path = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
    if file_path:
        output_paths = {
            'circle': [],
            'ellipse': [],
            'line': [],
            'polyline': [],
            'polygon': [],
            'rect': []
        }
        convert_svg(file_path, output_paths)
        for key, paths in output_paths.items():
            if paths:
                output_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")], initialfile=f"{key}.svg")
                if output_path:
                    with open(output_path, 'w') as file:
                        file.write('<?xml version="1.0" standalone="no"?>\n')
                        file.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" width="571" height="800" viewBox="0 0 571 800">\n')
                        for path in paths:
                            file.write(f'  <path id="{path["id"]}" d="{path["d"]}" stroke="{path["stroke"]}" stroke-opacity="{path["stroke-opacity"]}" stroke-width="{path["stroke-width"]}" fill="{path["fill"]}" />\n')
                        file.write('</svg>\n')

root = tk.Tk()
root.withdraw()  # Hide the root window

choose_file()
