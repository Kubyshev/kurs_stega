from PIL import Image
import numpy as np

# Загрузка изображения
image = Image.open('stego_block.bmp')

# Преобразование изображения в массив numpy
image_array = np.array(image)

# Выделение синего канала (третий канал в RGB)
blue_channel = image_array[:, :, 2]

# Размер изображения
height, width = blue_channel.shape
print(f"Размер изображения: {height}x{width}")

# Количество значений в блоке
block_size = 230

# Вычисление количества блоков
num_blocks = (height * width) // block_size
print(f"Количество блоков: {num_blocks}")

# Преобразование синего канала в одномерный массив
blue_channel_flat = blue_channel.flatten()

# Разделение на блоки по 230 значений
blocks = np.array_split(blue_channel_flat[:num_blocks * block_size], num_blocks)

# Сохранение блоков в текстовый файл
with open('blue_channel_blocks_stego.txt', 'w') as file:
    for block in blocks:
        # Преобразуем блок в строку с разделителем пробелом
        block_str = ' '.join(map(str, block))
        file.write(block_str + '\n')

print("Блоки успешно сохранены в файл 'blue_channel_blocks_stego.txt'.")