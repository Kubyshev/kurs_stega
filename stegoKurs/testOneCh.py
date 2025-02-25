import numpy as np
from PIL import Image
import qrcode


# Функция для генерации QR-кода и сохранения его в виде бинарного (черно-белого) изображения
def generate_qr_code(data, qr_path, qr_size=(200, 200)):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert('1')
    img = img.resize(qr_size)
    img.save(qr_path)


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


# Скрываем битовую строку в синем канале контейнерного изображения
def hide_data_in_blue_channel(image_path, data_bits, output_image_path):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    data_len = len(data_bits)
    data_index = 0

    for y in range(img.height):
        for x in range(img.width):
            if data_index >= data_len:
                break

            r, g, b = pixels[x, y]
            # Модифицируем только синий канал (b)
            b = (b & 0xFE) | int(data_bits[data_index])
            data_index += 1

            pixels[x, y] = (r, g, b)
        if data_index >= data_len:
            break

    img.save(output_image_path)
    print(f"Скрыто {data_index} бит из {data_len} бит в синем канале.")


# Извлечение битов из синего канала изображения
def extract_data_from_blue_channel(image_path, num_bits):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    extracted_bits = ""
    for y in range(img.height):
        for x in range(img.width):
            if len(extracted_bits) >= num_bits:
                break
            _, _, b = pixels[x, y]
            extracted_bits += str(b & 1)
        if len(extracted_bits) >= num_bits:
            break

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
    img1 = Image.open(image1_path).convert('RGB')
    img2 = Image.open(image2_path).convert('RGB')
    if img1.size != img2.size:
        raise ValueError("Изображения должны иметь одинаковые размеры!")

    width, height = img1.size


    pixels1 = img1.load()
    pixels2 = img2.load()

    # Сумма квадратов разностей
    sum_of_squares = 0.0

    # Перебираем все пиксели
    for y in range(height):
        for x in range(width):
            # Берём только синий канал (индекс 2)
            b1 = pixels1[x, y][2]
            b2 = pixels2[x, y][2]
            # Добавляем квадрат разности к сумме
            sum_of_squares += (b1 - b2) ** 2

    # Подставляем в формулу MSE
    mse = sum_of_squares / (width * height)
    return mse

def calculate_nmse(image1_path, image2_path):
    img1 = Image.open(image1_path).convert('RGB')
    width, height = img1.size
    pixels1 = img1.load()

    # Сумма квадратов значений синего канала
    sum_sq = 0.0
    for y in range(height):
        for x in range(width):
            b = pixels1[x, y][2]
            sum_sq += b ** 2

        # Средний квадрат значений синего канала
        mean_sq = sum_sq / (width * height)

        # Вычисляем MSE
        mse = calculate_mse(image1_path, image2_path)

        # Если mean_sq = 0 (все пиксели синего канала равны 0), NMSE становится бесконечностью
        if mean_sq == 0:
            nmse = float('inf')
        else:
            nmse = mse / mean_sq

        return nmse


# Пример использования:
if __name__ == '__main__':
    # 1. Генерируем QR-код с нужными данными
    data_for_qr = "Artem"
    qr_image_path = "qr_code.bmp"
    generate_qr_code(data_for_qr, qr_image_path, qr_size=(100, 100))

    # 2. Преобразуем QR-код в битовую строку
    qr_bits, qr_size = image_to_bits(qr_image_path)
    print(f"QR-код имеет размер {qr_size} и содержит {len(qr_bits)} бит")

    # 3. Скрываем данные (битовую строку) в контейнерном изображении только в синем канале
    container_image = "B.bmp"  # путь к контейнеру
    stego_image = "stego_blue.bmp"
    hide_data_in_blue_channel(container_image, qr_bits, stego_image)

    # 4. Извлекаем данные из синего канала
    extracted_bits = extract_data_from_blue_channel(stego_image, len(qr_bits))

    # 5. Восстанавливаем QR-код из извлечённых битов
    recovered_qr_image = "recovered_qr_blue.bmp"
    bits_to_image(extracted_bits, qr_size, recovered_qr_image)

    print("Процесс завершён. Проверьте файлы:", stego_image, recovered_qr_image)

    print( "MSE:", calculate_mse(container_image, stego_image))
    print("NMSE:", calculate_nmse(container_image, stego_image))