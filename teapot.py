import numpy as np
from PIL import Image

FILENAME = 'input/teapot1.obj'
OUTPUT_FILENAME = 'output/teapot_render.png'

N = 800
BACKGROUND = np.array([0, 0, 0], dtype=np.float64)
BASE_COLOR = np.array([255, 0, 220], dtype=np.float64)


def parse_float(item: str) -> float | str:
    try:
        return float(item)
    except:
        return item


def distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 +
            (point1[1] - point2[1]) ** 2 +
            (point1[2] - point2[2]) ** 2) ** 0.5


def bresenham(x0: int, y0: int, x1: int, y1: int):
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points


def project_to_pixels(vertices, size: int):
    if not vertices:
        return []

    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]

    max_abs = max(max(abs(x) for x in xs), max(abs(y) for y in ys), 1e-9)

    margin = 20                                 # отступ от края
    scale = (size / 2 - margin) / max_abs       # масштаб

    coords = []
    for x, y in zip(xs, ys):
        px = int(round(x * scale + size / 2))
        py = int(round(-y * scale + size / 2))
        coords.append((px, py))
    return coords


def render(vertices, faces, size: int = N) -> np.ndarray:
    img = np.zeros((size, size, 3), dtype=np.float64)
    img[:] = BACKGROUND

    coords = project_to_pixels(vertices, size)
    cx = cy = size / 2.0

    for face in faces:
        if any(i < 1 or i > len(coords) for i in face[:3]):
            continue

        pts = [coords[i - 1] for i in face[:3]]

        for j in range(3):
            x0, y0 = pts[j]
            x1, y1 = pts[(j + 1) % 3]

            for (px, py) in bresenham(x0, y0, x1, y1):
                if 0 <= px < size and 0 <= py < size:
                    d = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
                    factor = max(0.0, 1.0 - d / size)
                    color = BASE_COLOR * factor
                    img[py, px] = np.maximum(img[py, px], color)

    return np.clip(img, 0, 255).astype(np.uint8)


def main():
    vertices, faces, edges, vert_dict = [], [], set(), dict()

    with open(FILENAME, 'r', encoding='utf-8') as file:
        lines = list(map(lambda x: [parse_float(y) for y in x.strip().split()],
                         file.readlines()))

        for line in lines:
            if not line:
                continue
            if line[0] == 'v':
                vertices.append(tuple(line[1:]))
            else:
                faces.append(tuple(map(int, line[1:])))

    print(f'Вершин: {len(vertices)}')
    for i in range(len(vertices)):
        vert_dict.update({i: 0})
    for face in faces:
        vert_dict[face[0] - 1] += 1
        vert_dict[face[1] - 1] += 1
        vert_dict[face[2] - 1] += 1

        edge1 = (min(face[0], face[1]), max(face[0], face[1]))
        edge2 = (min(face[0], face[2]), max(face[0], face[2]))
        edge3 = (min(face[2], face[1]), max(face[2], face[1]))
        for edge in (edge1, edge2, edge3):
            edges.add(edge)

    total_length = 0
    for edge in edges:
        total_length += distance(vertices[edge[0] - 1], vertices[edge[1] - 1])

    most_frequent_vert = -1
    freq = -1
    for vert in vert_dict.items():
        if vert[1] > freq:
            most_frequent_vert = vert[0]
            freq = vert[1]

    print(f'Длина всех ребер: {total_length}\n'
          f'Вершина с самым большим кол-вом прилегающих граней({freq}) '
          f'- #{most_frequent_vert}')

    # === Отображение модели ===
    img = render(vertices, faces, N)
    Image.fromarray(img, mode='RGB').save(OUTPUT_FILENAME)
    Image.fromarray(img, mode='RGB').show()


if __name__ == '__main__':
    main()