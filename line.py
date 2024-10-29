#скрипт для линий
import tkinter as tk
from tkinter import filedialog
import re

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

def convert_svg(file_path, output_path):
    with open(file_path, 'r') as file:
        svg_data = file.read()

    paths = []
    lines = re.findall(r'<line[^>]+>', svg_data)

    for line in lines:
        x1 = float(re.search(r'x1="([^"]+)"', line).group(1))
        y1 = float(re.search(r'y1="([^"]+)"', line).group(1))
        x2 = float(re.search(r'x2="([^"]+)"', line).group(1))
        y2 = float(re.search(r'y2="([^"]+)"', line).group(1))
        stroke = re.search(r'stroke="([^"]+)"', line).group(1)
        stroke_width = re.search(r'stroke-width="([^"]+)"', line).group(1)
        stroke_opacity = re.search(r'stroke-opacity="([^"]+)"', line).group(1)
        elem_id = re.search(r'id="([^"]+)"', line).group(1)

        path = line_to_path(x1, y1, x2, y2, stroke, stroke_width, stroke_opacity, elem_id)
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
