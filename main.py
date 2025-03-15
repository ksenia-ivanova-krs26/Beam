import pandas as pd  # Для работы с Excel-файлами
import numpy as np  # Для числовых расчетов и работы с массивами
import matplotlib.pyplot as plt  # Графики
from beam_utils import Beam
from section import Section

def main():
    """
    Основная функция для выполнения расчетов и визуализации.
    """
    # Чтение данных из Excel-файла
    df = pd.read_excel('InputData.xlsx', sheet_name="Лист1", header=None)

    # Извлечение необходимых данных
    CS = df.iloc[0, 2:8].dropna().tolist()  # Названия сечений
    X = df.iloc[1, 2:8].values.astype(float)  # Координаты X
    E = df.iloc[2, 2:8].values.astype(float)  # Модуль Юнга
    A = df.iloc[3, 2:8].values.astype(float)  # Площади сечений
    # Извлечение нагрузок
    column_a = df[0]
    filtered_indices = column_a[column_a.str.contains('Расчетный случай', na=False)].index
    if not filtered_indices.empty:
        last_index = filtered_indices[-1]
    else:
        last_index = None

    loads = df.iloc[4:(last_index + 1), 2:8].values.astype(float)  # Нагрузки
    LC = [f'LC{i + 1}' for i in range(last_index)]  # Названия расчетных случаев

    #создание объекта сечений, описыващих балку
    section_data = Section(CS, X, E, A, loads, LC)

    # Создание объекта балки и передача всех подготовленных массивов 
    beam = Beam(section_data)

    # Расчет напряжений, коэффициентов запаса и минимального КЗ
    sigma_cr = 1.5  # Критическое напряжение (МПа)
    sigma = beam.calculate_sigma() # Расчет напряжений в каждом сечении для каждого расчетного случая
    MS = beam.calculate_MS(sigma, sigma_cr) # Расчет коэффициентов запаса
    # Визуализация результатов
    beam.plot_sigma(sigma, sigma_cr, MS)

# Проверка, что файл запущен напрямую (а не импортирован)
if __name__ == "__main__":
    main()