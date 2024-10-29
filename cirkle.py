#скрипт для кругов
import tkinter as tk
from tkinter import filedialog
import re

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

def convert_svg(file_path, output_path):
    with open(file_path, 'r') as file:
        svg_data = file.read()

    paths = []
    circles = re.findall(r'<circle[^>]+>', svg_data)

    for circle in circles:
        cx = float(re.search(r'cx="([^"]+)"', circle).group(1))
        cy = float(re.search(r'cy="([^"]+)"', circle).group(1))
        r = float(re.search(r'r="([^"]+)"', circle).group(1))
        fill = re.search(r'fill="([^"]+)"', circle).group(1)
        fill_opacity = re.search(r'fill-opacity="([^"]+)"', circle).group(1)
        elem_id = re.search(r'id="([^"]+)"', circle).group(1)

        path = circle_to_path(cx, cy, r, fill, fill_opacity, elem_id)
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
