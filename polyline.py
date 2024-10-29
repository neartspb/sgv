#скрипт для полилиний
import tkinter as tk
from tkinter import filedialog
import re

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

def convert_svg(file_path, output_path):
    with open(file_path, 'r') as file:
        svg_data = file.read()

    paths = []
    polylines = re.findall(r'<polyline[^>]+>', svg_data)

    for polyline in polylines:
        points = re.search(r'points="([^"]+)"', polyline).group(1).split()
        stroke = re.search(r'stroke="([^"]+)"', polyline).group(1)
        stroke_width = re.search(r'stroke-width="([^"]+)"', polyline).group(1)
        stroke_opacity = re.search(r'stroke-opacity="([^"]+)"', polyline).group(1)
        elem_id = re.search(r'id="([^"]+)"', polyline).group(1)

        path = polyline_to_path(points, stroke, stroke_width, stroke_opacity, elem_id)
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
