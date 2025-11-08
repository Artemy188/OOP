import math
import pandas as pd


def transform_sirius_coordinates(input_file="roads.txt", output_file="transformed_roads.txt"):
    """
    Преобразование координат Сириуса с учетом широты 40°
    """
    # Коэффициент для 40° широты
    lat_sirius = 40.0
    lon_scale_factor = 1 / math.cos(math.radians(lat_sirius))

    print(f"Коэффициент преобразования долготы: {lon_scale_factor:.6f}")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Разделяем на узлы и ребра
    nodes_section, edges_section = content.split("Рёбра графа (с названиями улиц):")

    # Обрабатываем узлы
    transformed_nodes = []
    nodes_lines = nodes_section.split("ID: ")[1:]  # Пропускаем заголовок

    for node_line in nodes_lines:
        if not node_line.strip():
            continue

        # Парсим строку узла
        parts = node_line.split(", координаты: ")
        node_id = parts[0].strip()
        coords = parts[1].strip()

        lon, lat = map(float, coords.split(", "))

        # Применяем преобразование только к долготе
        lon_transformed = lon * lon_scale_factor

        transformed_nodes.append(f"ID: {node_id}, координаты: {lat:.7f}, {lon_transformed:.7f}")

    # Сохраняем преобразованные данные
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Узлы графа (преобразованные):\n")
        f.write("\n".join(transformed_nodes))
        f.write(f"\n\nРёбра графа (с названиями улиц):\n{edges_section}")

    print(f"Преобразованные координаты сохранены в {output_file}")
    return output_file


# Запускаем преобразование
transformed_file = transform_sirius_coordinates()