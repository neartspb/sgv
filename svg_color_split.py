import svgwrite
from xml.dom import minidom
from tkinter import Tk, Button, filedialog, Label, Listbox, EXTENDED, Scrollbar, Frame

# Функция для анализа строк в SVG файле и сохранения их в новый SVG файл
def analyze_paths(input_file):
    doc = minidom.parse(input_file)
    paths = doc.getElementsByTagName('path')
    rect = doc.getElementsByTagName('rect')[0]
    svg_elem = doc.getElementsByTagName('svg')[0]
    width = svg_elem.getAttribute('width')
    height = svg_elem.getAttribute('height')
    path_data = []
    for idx, path in enumerate(paths):
        color = path.getAttribute('stroke')
        if color.startswith('rgb'):
            path_data.append((idx, color, path))
    path_data.sort(key=lambda item: color_brightness(tuple(map(int, item[1][4:-1].split(',')))))
    dwg = svgwrite.Drawing('path_data.svg', profile=svg_elem.getAttribute('baseProfile'), size=(width, height), viewBox=svg_elem.getAttribute('viewBox'))
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=rect.getAttribute('fill'), fill_opacity=rect.getAttribute('fill-opacity')))
    # Добавляем опорные точки
    dwg.add(dwg.path(d=f"M0,0 L1,0 L1,1 L0,1 Z", fill="black"))
    dwg.add(dwg.path(d=f"M{int(width)-1},0 L{width},0 L{width},1 L{int(width)-1},1 Z", fill="black"))
    dwg.add(dwg.path(d=f"M0,{int(height)-1} L1,{int(height)-1} L1,{height} L0,{height} Z", fill="black"))
    dwg.add(dwg.path(d=f"M{int(width)-1},{int(height)-1} L{width},{int(height)-1} L{width},{height} L{int(width)-1},{height} Z", fill="black"))
    for idx, color, path in path_data:
        dwg.add(dwg.path(d=path.getAttribute('d'), stroke=color, fill='none'))
    dwg.save()

# Функция для определения яркости цвета
def color_brightness(rgb):
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

# Функция для обработки SVG файла
def process_svg(input_file, selected_indices, group_counter):
    doc = minidom.parse(input_file)
    paths = doc.getElementsByTagName('path')
    rect = doc.getElementsByTagName('rect')[0]
    svg_elem = doc.getElementsByTagName('svg')[0]
    width = svg_elem.getAttribute('width')
    height = svg_elem.getAttribute('height')
    selected_paths = [paths[i] for i in selected_indices]
    output_file = f"selected_paths_group_{group_counter}.svg"
    dwg = svgwrite.Drawing(output_file, profile=svg_elem.getAttribute('baseProfile'), size=(width, height), viewBox=svg_elem.getAttribute('viewBox'))
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=rect.getAttribute('fill'), fill_opacity=rect.getAttribute('fill-opacity')))
    # Добавляем опорные точки
    dwg.add(dwg.path(d=f"M0,0 L1,0 L1,1 L0,1 Z", fill="black"))
    dwg.add(dwg.path(d=f"M{int(width)-1},0 L{width},0 L{width},1 L{int(width)-1},1 Z", fill="black"))
    dwg.add(dwg.path(d=f"M0,{int(height)-1} L1,{int(height)-1} L1,{height} L0,{height} Z", fill="black"))
    dwg.add(dwg.path(d=f"M{int(width)-1},{int(height)-1} L{width},{int(height)-1} L{width},{height} L{int(width)-1},{height} Z", fill="black"))
    with open("all_paths.txt", "a") as all_paths_file:
        for path in selected_paths:
            dwg.add(dwg.path(d=path.getAttribute('d'), stroke=path.getAttribute('stroke'), fill='none'))
            all_paths_file.write(f"{path.toxml()}\n")
            print(f"Записана строка: {path.toxml()}")  # Отладочный вывод
    dwg.save(pretty=True)  # Добавляем параметр pretty=True для форматирования
    print(f"Сохранено {len(selected_paths)} строк в файл {output_file}.")

# Функция для обновления SVG файла после сохранения
def update_path_data(selected_indices):
    doc = minidom.parse('path_data.svg')
    paths = doc.getElementsByTagName('path')
    for i in selected_indices:
        paths[i].parentNode.removeChild(paths[i])
    with open('path_data.svg', 'w') as file:
        file.write(doc.toxml())

# Функция для загрузки данных из SVG файла в Listbox
def load_path_data(listbox):
    doc = minidom.parse('path_data.svg')
    paths = doc.getElementsByTagName('path')
    for idx, path in enumerate(paths):
        color = path.getAttribute('stroke')
        try:
            rgb_values = color[4:-1].split(',')
            if len(rgb_values) == 3:
                rgb = tuple(map(int, rgb_values))
                hex_color = '#%02x%02x%02x' % rgb
                listbox.insert("end", f"{idx}: {color}")
                listbox.itemconfig("end", {'bg': hex_color, 'fg': 'white' if color_brightness(rgb) < 128 else 'black'})
            else:
                print(f"Некорректный формат цвета: {color}")
        except ValueError:
            print(f"Ошибка разбора цвета: {color}")

# Создаем графический интерфейс
def create_gui():
    root = Tk()
    root.title("SVG Color Splitter")
    root.geometry("400x800")

    def open_file():
        input_file = filedialog.askopenfilename(title="Выберите входной SVG файл", filetypes=[("SVG files", "*.svg")])
        if input_file:
            analyze_paths(input_file)
            load_path_data(listbox)

    def reload_colors():
        listbox.delete(0, 'end')
        load_path_data(listbox)

    frame = Frame(root)
    frame.pack(fill="both", expand=True)
    scrollbar = Scrollbar(frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    listbox = Listbox(frame, selectmode=EXTENDED, yscrollcommand=scrollbar.set)
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)
    group_counter = 1

    def save_group():
        nonlocal group_counter
        selected_indices = listbox.curselection()
        if selected_indices:
            selected_indices = [int(listbox.get(i).split(":")[0]) for i in selected_indices]
            process_svg('path_data.svg', selected_indices, group_counter)
            update_path_data(selected_indices)
            print(f"Сохранено {len(selected_indices)} строк в группу {group_counter}!")
            group_counter += 1
            root.update_idletasks()  # Обновляем интерфейс
            listbox.selection_clear(0, 'end')  # Очищаем выделение после сохранения

    Label(root, text="Выберите SVG файл для разделения по цветам").pack(pady=10)
    Button(root, text="Открыть файл", command=open_file).pack(pady=5)
    Button(root, text="Сохранить группу", command=save_group).pack(pady=5)
    Button(root, text="Перезагрузить цвета", command=reload_colors).pack(pady=5)
    Button(root, text="Выход", command=root.quit).pack(pady=5)
    root.mainloop()

create_gui()
