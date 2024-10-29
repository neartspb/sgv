#скрипт для наклонных элипсов
import tkinter as tk
from tkinter import filedialog
import re
import math

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

def transform_point(x, y, translate, rotate, scale):
    # Применение масштабирования
    x *= scale[0]
    y *= scale[1]

    # Применение поворота
    rad_rotate = math.radians(rotate)
    x_rot = x * math.cos(rad_rotate) - y * math.sin(rad_rotate)
    y_rot = x * math.sin(rad_rotate) + y * math.cos(rad_rotate)

    # Применение трансляции
    x_trans = x_rot + translate[0]
    y_trans = y_rot + translate[1]

    return x_trans, y_trans

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

def convert_svg(file_path, output_path):
    with open(file_path, 'r') as file:
        svg_data = file.read()

    paths = []
    groups = re.findall(r'<g[^>]*transform="([^"]+)"[^>]*>(.*?)</g>', svg_data, re.DOTALL)

    for group_transform, group_content in groups:
        ellipses = re.findall(r'<ellipse[^>]+>', group_content)
        for ellipse in ellipses:
            cx = float(re.search(r'cx="([^"]+)"', ellipse).group(1))
            cy = float(re.search(r'cy="([^"]+)"', ellipse).group(1))
            rx = float(re.search(r'rx="([^"]+)"', ellipse).group(1))
            ry = float(re.search(r'ry="([^"]+)"', ellipse).group(1))
            fill = re.search(r'fill="([^"]+)"', ellipse).group(1)
            fill_opacity = re.search(r'fill-opacity="([^"]+)"', ellipse).group(1)
            elem_id = re.search(r'id="([^"]+)"', ellipse).group(1)

            points = ellipse_to_polygon(cx, cy, rx, ry, group_transform)
            path = polygon_to_path(points, fill, fill_opacity, elem_id)
            paths.append(path)

    with open(output_path, 'w') as file:
        file.write('<?xml version="1.0" standalone="no"?>\n')
        file.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.2" baseProfile="tiny" width="571" height="800" viewBox="0 0 571 800">\n')
        for path in paths:
            file.write(f'  <path id="{path["id"]}" d="{path["d"]}" stroke="{path["stroke"]}" stroke-opacity="{path["stroke-opacity"]}" stroke-width="{path["stroke-width"]}" fill="{path["fill"]}" />\n')
        file.write('</svg>\n')

def choose_file():
    root.update()  # Ensure dialog opens on top
    file_path = filedialog.askopenfilename(filetypes=[("SVG files", "*.svg")])
    if file_path:
        output_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=[("SVG files", "*.svg")])
        if output_path:
            convert_svg(file_path, output_path)

root = tk.Tk()
root.withdraw()  # Hide the root window

choose_file()
