#скрипт для прямоугольников
import tkinter as tk
from tkinter import filedialog
import re

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

def convert_svg(file_path, output_path):
    with open(file_path, 'r') as file:
        svg_data = file.read()

    paths = []
    rects = re.findall(r'<rect[^>]+>', svg_data)

    for rect in rects:
        x = float(re.search(r'x="([^"]+)"', rect).group(1))
        y = float(re.search(r'y="([^"]+)"', rect).group(1))
        width = float(re.search(r'width="([^"]+)"', rect).group(1))
        height = float(re.search(r'height="([^"]+)"', rect).group(1))
        fill = re.search(r'fill="([^"]+)"', rect).group(1)
        fill_opacity = re.search(r'fill-opacity="([^"]+)"', rect).group(1)
        elem_id = re.search(r'id="([^"]+)"', rect).group(1)

        path = rect_to_path(x, y, width, height, fill, fill_opacity, elem_id)
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
