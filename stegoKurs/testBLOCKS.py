import numpy as np
from PIL import Image
import qrcode


# Преобразуем изображение (QR-код) в строку битов.
def image_to_bits(image_path):
    img = Image.open(image_path)
    img = img.convert('1')  # черно-белое изображение
    pixels = img.load()
    bits = ""
    for y in range(img.height):
        for x in range(img.width):
            # В режиме '1': 0 – черный, 255 – белый.
            bit = '0' if pixels[x, y] == 0 else '1'
            bits += bit
    return bits, img.size  # возвращаем также размеры для восстановления


# Скрываем битовую строку в синем канале контейнерного изображения блоками
def hide_data_in_blue_channel(image_path, data_bits, output_image_path, block_size=230):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    data_len = len(data_bits)
    data_index = 0

    for y in range(img.height):
        for x in range(img.width):
            if data_index >= data_len * block_size:
                break

            # Определяем, какой бит данных записываем
            bit_index = data_index // block_size
            if bit_index >= data_len:
                break

            # Модифицируем только синий канал (b)
            r, g, b = pixels[x, y]
            b = (b & 0xFE) | int(data_bits[bit_index])
            pixels[x, y] = (r, g, b)

            data_index += 1

    img.save(output_image_path)
    print(f"Скрыто {data_len} бит данных в синем канале блоками по {block_size} пикселей.")


# Извлечение битов из синего канала изображения блоками
def extract_data_from_blue_channel(image_path, num_bits, block_size=230):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    extracted_bits = ""
    for i in range(num_bits):
        bit_sum = 0
        for j in range(block_size):
            x = (i * block_size + j) % img.width
            y = (i * block_size + j) // img.width
            if y >= img.height:
                break
            _, _, b = pixels[x, y]
            bit_sum += b & 1

        # Мажоритарное голосование: если большинство пикселей имеют 1, то извлеченный бит 1
        extracted_bit = '1' if bit_sum > block_size // 2 else '0'
        extracted_bits += extracted_bit

    return extracted_bits


# Восстановление изображения QR-кода из битовой строки
def bits_to_image(bits, size, output_path):
    width, height = size
    img = Image.new('1', (width, height))
    pixels = img.load()

    index = 0
    for y in range(height):
        for x in range(width):
            if index < len(bits):
                pixels[x, y] = 0 if bits[index] == '0' else 255
                index += 1
            else:
                break
    img.save(output_path)

def calculate_mse(image1_path, image2_path):
    img1 = np.array(Image.open(image1_path).convert('RGB'), dtype=np.float64)
    img2 = np.array(Image.open(image2_path).convert('RGB'), dtype=np.float64)

    mse = np.mean((img1 - img2) ** 2, axis=(0, 1))  # MSE для каждого канала
    return np.mean(mse)  # Среднее значение по каналам (общий MSE)

def calculate_nmse(image1_path, image2_path):
    img1 = np.array(Image.open(image1_path).convert('RGB'), dtype=np.float64)
    img2 = np.array(Image.open(image2_path).convert('RGB'), dtype=np.float64)

    nmse = np.sum((img1 - img2) ** 2, axis=(0, 1)) / np.sum(img1 ** 2, axis=(0, 1))  # NMSE по каналам
    return np.mean(nmse)  # Среднее значение по каналам (общий NMSE)


# Пример использования:
if __name__ == '__main__':
    # 1. Генерируем QR-код с нужными данными
    data_for_qr = "КубышевАртём"
    qr_image_path = "qr_code.bmp"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_for_qr)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img = img.resize((100, 100))
    img.save(qr_image_path)

    # 2. Преобразуем QR-код в битовую строку
    qr_bits, qr_size = image_to_bits(qr_image_path)
    print(f"QR-код имеет размер {qr_size} и содержит {len(qr_bits)} бит")

    # 3. Скрываем данные (битовую строку) в контейнерном изображении блоками
    container_image = "B.bmp"  # путь к контейнеру
    stego_image = "stego_block.bmp"
    hide_data_in_blue_channel(container_image, qr_bits, stego_image, block_size=230)

    # 4. Извлекаем данные из синего канала блоками
    extracted_bits = extract_data_from_blue_channel(stego_image, len(qr_bits), block_size=230)

    # 5. Проверяем корректность извлеченных данных
    if qr_bits == extracted_bits:
        print("Данные извлечены корректно.")
    else:
        print("Ошибка: извлеченные данные не совпадают с исходными.")
        print(f"Первые 50 бит исходных данных: {qr_bits[:50]}")
        print(f"Первые 50 бит извлеченных данных: {extracted_bits[:50]}")

    # 6. Восстанавливаем QR-код из извлечённых битов
    recovered_qr_image = "recovered_qr_block.bmp"
    bits_to_image(extracted_bits, qr_size, recovered_qr_image)

    print("Процесс завершён. Проверьте файлы:", stego_image, recovered_qr_image)
    print( "MSE:", calculate_mse(container_image, stego_image))
    print("NMSE:", calculate_nmse(container_image, stego_image))