import numpy as np
import matplotlib.pyplot as plt  # Графики
from typing import List, Sequence # Для аннотации типов данных 

class Section:
    def __init__(
        self,
        CS: List[str],  # Список названий сечений (например, ['A-A', 'B-B'])
        X: Sequence[float],  # Массив координат X сечений (может быть list или tuple)
        E: Sequence[float],  # Массив значений модуля Юнга в сечении
        A: Sequence[float],  # Массив площадей поперечных сечений
        loads: np.ndarray,  # 2D-массив нагрузок (строки - расчетные случаи, столбцы - сечения)
        LC: List[str]  # Список названий расчетных случаев
    ):
        """
        Конструктор класса Section
        :param CS: список названий сечений (например, ['A-A', 'B-B'])
        :param X: массив координат X сечений
        :param E: массив значений модуля Юнга в сечении
        :param A: массив площадей поперечных сечений
        :param loads: 2D-массив нагрузок (строки - расчетные случаи, столбцы - сечения)
        :param LC: список названий расчетных случаев
        """
        self.CS = CS  # Сохраняем названия сечений
        self.X = X  # Сохраняем координаты X сечений
        self.E = E  # Сохраняем массив значений модуля Юнга в сечении
        self.A = A  # Сохраняем площади сечений
        self.loads = loads  # Сохраняем нагрузки (форма: [нагрузки, расчетные_случаи, сечения])
        self.LC = LC  # Сохраняем названия расчетных случаев
