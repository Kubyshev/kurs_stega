from PIL import Image

image_path='stego.bmp'
def get_rgb_matrix(image_path):
    # Открываем изображение
    image = Image.open(image_path)

    # Преобразуем изображение в режим RGB (если оно не в этом режиме)
    image = image.convert('RGB')

    # Получаем размеры изображения
    width, height = image.size

    # Создаем пустую матрицу для хранения RGB значений
    rgb_matrix = []

    # Проходим по каждому пикселю изображения
    for y in range(height):
        row = []
        for x in range(width):
            # Получаем RGB значения пикселя
            r, g, b = image.getpixel((x, y))
            row.append((r, g, b))
        rgb_matrix.append(row)

    return rgb_matrix
# Получаем матрицу RGB
rgb_matrix = get_rgb_matrix(image_path)

# Выводим результат (например, первые 5 строк и 5 столбцов)
for column in rgb_matrix[:100]:
    print(column[:100])