import numpy as np
import matplotlib.pyplot as plt
from section import Section
from typing import List # Для аннотации типов данных 

class Beam:
    def __init__(self, section: Section):
        """
        Конструктор класса Beam
        :param section: объект класса Section, содержащий данные о сечениях
        self,
        CS: List[str],  # Список названий сечений (например, ['A-A', 'B-B'])
        X: Sequence[float],  # Массив координат X сечений (может быть list или tuple)
        E: Sequence[float],  # Массив значений модуля Юнга в сечении
        A: Sequence[float],  # Массив площадей поперечных сечений
        loads: np.ndarray,  # 2D-массив нагрузок (строки - расчетные случаи, столбцы - сечения)
        LC: List[str]  # Список названий расчетных случаев
        """
        self.section = section  # Сохраняем объект Section

    def calculate_sigma (self):
        """
        Рассчитывает напряжения для всех расчетных случаев.
        :return: 2D-массив массив напряжений [расчетные случаи, сечения]
        """
        # Преобразуем данные в NumPy массивы
        loads = np.array(self.section.loads)  # 2D-массив нагрузок        
        E = np.array(self.section.E)         # 1D-массив модулей Юнга
        A = np.array(self.section.A)         # 1D-массив площадей поперечных сечений

        return loads / (E * A)
    
    def calculate_MS(self, sigma: np.ndarray, sigma_cr: int):
        """
        Рассчитывает запас прочности для всех расчетных случаев.
        :param sigma: 2D-массив напряжений [расчетные случаи, сечения]
        :param sigma_cr: критическое напряжение
        :return: 2D-массив запасов прочности       
        """
        return sigma / sigma_cr
    
    def find_min_MS(self, MS: np.ndarray):
        """
        Находит минимальный запас прочности и соответствующие ему координату сечения и расчетный случай.
        :param MS: 2D-массив запасов прочности [расчетные случаи, сечения]
        :return: минимальный запас прочности, координата сечения, название расчетного случая
        """
        # Преобразуем MS в numpy массив 
        MS = np.array(MS)

        # Находим минимальное значение и его индекс
        MSmin = np.min(MS)
        MSmin_index = np.argmin(MS)

        # Вычисляем индексы расчетного случая (LC) и сечения (X)
        LC_index = MSmin_index // MS.shape[1]  # Индекс строки (расчетный случай)
        CS_index = MSmin_index % MS.shape[1]   # Индекс столбца (сечение)

        # Получаем координату сечения и название расчетного случая
        section_X = self.section.X[CS_index]
        LC_name = self.section.LC[LC_index]

        # Возвращаем результат
        return MSmin, section_X, LC_name

    def plot_sigma(self, stresses: np.ndarray, sigma_cr: float, MS: np.ndarray):
        """
        Строит эпюры напряжений для всех расчетных случаев и добавляет информацию о минимальном запасе прочности.
        :param stresses: 2D-массив напряжений [расчетные случаи, сечения]
        :param sigma_cr: критическое напряжение
        :param MS: 2D-массив запасов прочности [расчетные случаи, сечения]
        """
        # Находим минимальный запас прочности и связанные данные
        MSmin, section_X, LC_name = self.find_min_MS(MS)

        # Создаем график
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.canvas.manager.set_window_title("Эпюры напряжений")

        # Создаем список линий и их меток
        lines = []
        for i in range(stresses.shape[0]):
            line, = ax.plot(self.section.X, stresses[i], label=self.section.LC[i])
            lines.append(line)

        # Добавляем горизонтальную линию для критического напряжения
        ax.axhline(y=sigma_cr, color='r', linestyle='--', label=f'Критическое напряжение ({sigma_cr} МПа)')

        # Настройка графика
        ax.set_xlabel('Координата X')
        ax.set_ylabel('Напряжение, МПа')
        ax.set_title('Эпюры напряжений для всех расчетных случаев')
        legend = ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')  # Легенда справа от графика

        # Добавляем текстовую аннотацию с минимальным запасом прочности
        annotation_text = (
            f"Минимальный КЗ: {MSmin:.2f}\n"
            f"Координата X: {section_X:.1f}\n"
            f"Расчетный случай: {LC_name}"
        )
        fig.text(
            1.2, 0.1, annotation_text,
            transform=ax.transAxes,  # Относительно осей графика
            fontsize=10, color='blue',
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="gray")
        )

        # Обработчик событий для кликов на тексте легенды
        def on_legend_click(event):
            # Проверяем, что клик был внутри области легенды
            if legend.get_window_extent().contains(event.x, event.y):
                # Определяем, на какой текст легенды кликнули
                for text, handle in zip(legend.get_texts(), legend.legend_handles):
                    if text.get_window_extent().contains(event.x, event.y):
                        label = text.get_text()  # Получаем метку LCi
                        break
                else:
                    return  # Если клик не попал на текст, выходим

                # Находим соответствующую линию
                for line, handle, text in zip(lines, legend.legend_handles, legend.get_texts()):
                    if line.get_label() == label:
                        # Переключаем видимость линии
                        visible = not line.get_visible()
                        line.set_visible(visible)
                        
                        # Изменяем цвет текста легенды
                        text.set_color('gray' if not visible else 'black')
                        
                        # Изменяем цвет маркера в легенде
                        handle.set_color('gray' if not visible else line.get_color())
                        handle.set_alpha(0.2 if not visible else 1.0)
                        break

                # Обновляем график
                fig.canvas.draw()

        # Подключаем обработчик событий
        fig.canvas.mpl_connect('button_press_event', on_legend_click)

        # Настройка макета
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    