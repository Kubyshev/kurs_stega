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
    img1 = np.array(Image.open(image1_path).convert('RGB'), dtype=np.float64)
    img2 = np.array(Image.open(image2_path).convert('RGB'), dtype=np.float64)

    mse = np.mean((img1 - img2) ** 2, axis=(0, 1))  # MSE для каждого канала
    return np.mean(mse)  # Среднее значение по каналам (общий MSE)

def calculate_nmse(image1_path, image2_path):
    img1 = np.array(Image.open(image1_path).convert('RGB'), dtype=np.float64)
    img2 = np.array(Image.open(image2_path).convert('RGB'), dtype=np.float64)

    nmse = np.sum((img1 - img2) ** 2, axis=(0, 1)) / np.sum(img1 ** 2, axis=(0, 1))  # NMSE по каналам
    return np.mean(nmse)  # Среднее значение по каналам (общий NMSE)




def get_image_memory_size(file_path):
    img = Image.open(file_path)
    img_array = np.array(img)

    # Размер = высота * ширина * количество каналов (RGB = 3 байта на пиксель)
    size_in_bytes = img_array.nbytes
    #print(f"📏 Реальный размер изображения в памяти: {size_in_bytes} байт")
    return size_in_bytes


# Пример использования:
if __name__ == '__main__':
    # 1. Генерируем QR-код с нужными данными
    data_for_qr = "КубышевАртём"
    qr_image_path = "qr_code.bmp"
    generate_qr_code(data_for_qr, qr_image_path, qr_size=(100, 100))

    # 2. Преобразуем QR-код в битовую строку
    qr_bits, qr_size = image_to_bits(qr_image_path)
    print(f"QR-код имеет размер {qr_size} и содержит {len(qr_bits)} бит")
    #print(qr_bits)

    # 2.1 Compare size qr and image.
    get_image_memory_size("qr_code.bmp")
    get_image_memory_size("B.bmp")
    if get_image_memory_size("B.bmp") > 8*get_image_memory_size("qr_code.bmp"):
        print("Размер изображения удовлетвояет условию скрытия")
    else:
        breakpoint()

    # 3. Скрываем данные (битовую строку) в контейнерном изображении только в синем канале
    container_image = "B.bmp"  # путь к контейнеру
    stego_image = "stego.bmp"
    hide_data_in_blue_channel(container_image, qr_bits, stego_image)

    # 4. Извлекаем данные из синего канала
    extracted_bits = extract_data_from_blue_channel(stego_image, len(qr_bits))
    #print(extracted_bits)

    # 5. Восстанавливаем QR-код из извлечённых битов
    recovered_qr_image = "recovered_qr.bmp"
    bits_to_image(extracted_bits, qr_size, recovered_qr_image)

    print("Процесс завершён. Проверьте файлы:", stego_image, recovered_qr_image)

    print( "MSE:", calculate_mse(container_image, stego_image))
    print("NMSE:", calculate_nmse(container_image, stego_image))