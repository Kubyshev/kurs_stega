from PIL import Image
import qrcode
from qrcode import QRCode
import numpy as np

# Функция для генерации QR-кода и сохранения его в виде бинарного изображения (черно-белое)
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
    img = img.convert('1')  # Черно-белое изображение
    pixels = img.load()
    bits = ""
    for y in range(img.height):
        for x in range(img.width):
            # В режиме '1': значение пикселя 0 = черный, 255 = белый.
            # Преобразуем в бит: 0 -> 0, 255 -> 1.
            bit = '0' if pixels[x, y] == 0 else '1'
            bits += bit
    return bits, img.size  # возвращаем также размеры для восстановления


# Скрываем битовую строку в контейнерном изображении
def hide_data(image_path, data_bits, output_image_path):
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
            # Изменяем младший бит каждого канала, если есть данные
            if data_index < data_len:
                r = (r & 0xFE) | int(data_bits[data_index])
                data_index += 1
            if data_index < data_len:
                g = (g & 0xFE) | int(data_bits[data_index])
                data_index += 1
            if data_index < data_len:
                b = (b & 0xFE) | int(data_bits[data_index])
                data_index += 1

            pixels[x, y] = (r, g, b)
        if data_index >= data_len:
            break

    img.save(output_image_path)
    print(f"Скрыто {data_index} бит из {data_len} бит")


# Извлечение битов из изображения
def extract_data(image_path, num_bits):
    img = Image.open(image_path)
    img = img.convert('RGB')
    pixels = img.load()

    extracted_bits = ""
    for y in range(img.height):
        for x in range(img.width):
            if len(extracted_bits) >= num_bits:
                break
            r, g, b = pixels[x, y]
            extracted_bits += str(r & 1)
            if len(extracted_bits) >= num_bits:
                break
            extracted_bits += str(g & 1)
            if len(extracted_bits) >= num_bits:
                break
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
                # В режиме '1' значение 0 – черный, 1 – белый.
                pixels[x, y] = 0 if bits[index] == '0' else 255
                index += 1
            else:
                break
    img.save(output_path)

#Определение размеров изоюражения
def get_image_memory_size(file_path):
    img = Image.open(file_path)
    img_array = np.array(img)

    # Размер = высота * ширина * количество каналов (RGB = 3 байта на пиксель)
    size_in_bytes = img_array.nbytes
    #print(f"📏 Реальный размер изображения в памяти: {size_in_bytes} байт")
    return size_in_bytes

def compare_images(img1_path, img2_path):
    # Загружаем изображения
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")

    # Преобразуем в массивы NumPy
    img1_array = np.array(img1, dtype=np.int16)
    img2_array = np.array(img2, dtype=np.int16)

    # Проверяем размеры изображений
    if img1_array.shape != img2_array.shape:
        raise ValueError("❌ Изображения имеют разные размеры!")

    # Вычисляем разницу между пикселями
    diff = np.abs(img1_array - img2_array)

    # Подсчет количества отличающихся пикселей
    different_pixels = np.sum(diff > 0)
    total_pixels = img1_array.size // 3  # Три канала (RGB)
    print(f"🔍 Различий: {different_pixels} пикселей из {total_pixels}")


# Пример использования:
if __name__ == '__main__':
    # 1. Генерируем QR-код с нужными данными
    data_for_qr = "КубышевАртём"
    qr_image_path = "qr_code.bmp"
    generate_qr_code(data_for_qr, qr_image_path, qr_size=(100, 100))

    # 2. Преобразуем QR-код в битовую строку
    qr_bits, qr_size = image_to_bits(qr_image_path)
    print(f"QR код имеет размер {qr_size} и содержит {len(qr_bits)} бит")

    #2.1 Compare size qr and image.
    get_image_memory_size("qr_code.bmp")
    get_image_memory_size("B.bmp")
    if get_image_memory_size("B.bmp") > get_image_memory_size("qr_code.bmp"):
        print("Размер изображения удовлетвояет условию скрытия")
    else:
        breakpoint()

    # 3. Скрываем данные (битовую строку) в контейнерном изображении
    container_image = "B.bmp"  # убедитесь, что изображение достаточно большое
    stego_image = "stego.bmp"
    hide_data(container_image, qr_bits, stego_image)

    # 3.1 Get size image.bmp and stego.bmp and compare size differents
    #print(get_image_memory_size("B.bmp"))
    get_image_memory_size("stego.bmp")

    # 4. Извлекаем данные
    extracted_bits = extract_data(stego_image, len(qr_bits))

    # 5. Восстанавливаем QR-код из извлеченных битов
    recovered_qr_image = "recovered_qr.bmp"
    bits_to_image(extracted_bits, qr_size, recovered_qr_image)

    print("Процесс завершен. Проверьте файлы:", stego_image, recovered_qr_image)
    #5.1 Сравнение попиксельно в стегоконтейнере и изначальном изображении
    compare_images("B.bmp","stego.bmp")