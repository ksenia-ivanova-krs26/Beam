import pandas as pd  # Для работы с Excel-файлами
import numpy as np  # Для числовых расчетов и работы с массивами
import matplotlib.pyplot as plt  # Графики
from matplotlib.widgets import Button

class Beam:
    def __init__(self, section_names, X, A, loads, LC_names):
        """
        Конструктор класса Beam
        :param section_names: список названий сечений (например, ['A-A', 'B-B'])
        :param X: массив координат X сечений
        :param A: массив площадей поперечных сечений
        :param loads: 2D-массив нагрузок (строки - расчетные случаи, столбцы - сечения)
        :param LC_names: список названий расчетных случаев
        """
        self.section_names = section_names  # Сохраняем названия сечений
        self.X = X  # Сохраняем координаты X
        self.A = A  # Сохраняем площади сечений
        self.loads = loads  # Сохраняем нагрузки (форма: [нагрузки, расчетные_случаи, сечения])
        self.LC_names = LC_names  # Сохраняем названия расчетных случаев

    def calculate_stresses(self):
        """
        Рассчитывает напряжения для всех расчетных случаев и сечений
        :return: 2D-массив напряжений (строки - расчетные случаи, столбцы - сечения)
        """
        return (self.loads / self.A) / 1e6  # МПа (по условию задачи)

    def calculate_ms(self, sigma_cr, stresses):
        """
        Рассчитывает коэффициенты запаса прочности
        :param sigma_cr: критическое напряжение
        :param stresses: массив напряжений (результат calculate_stresses)
        :return: 2D-массив коэффициентов запаса
        """
        return sigma_cr / stresses  # Безразмерная величина

    def find_min_ms(self, ms):
        """
        Находит все минимальные коэффициенты запаса и соответствующие параметры
        :param ms: массив коэффициентов запаса (2D: [расчетные_случаи, сечения])
        :return: список кортежей (мин_значение, название_сечения, название_расчетного_случая)
        """
        min_value = np.min(ms)  # Находим глобальный минимум
        indices = np.argwhere(ms == min_value)  # Получаем все пары индексов (расчетный_случай, сечение)

        results = []
        for (lc_idx, sec_idx) in indices:
            results.append(
                (min_value,
                 self.section_names[sec_idx],
                 self.LC_names[lc_idx])
            )

        return results

    def plot_stresses(self, stresses, sigma_cr):
        """
        Строит эпюры напряжений с интерактивной легендой.
        При клике на метку в легенде соответствующая кривая и вертикальные линии скрываются или становятся видимыми.
        При наведении курсора на область легенды появляется подсказка.
        """
        # Создаем основное окно графика
        fig = plt.figure(figsize=(16, 8))  # Устанавливаем размер окна графика

        # Основная область графика
        ax = fig.add_axes([0.1, 0.1, 0.6, 0.8])  # [left, bottom, width, height]
        # `ax` — это основная область для отображения графиков.

        # Хранение линий графиков и вертикальных линий
        lines = []  # Список для хранения основных линий графиков
        vertical_lines = []  # Список списков вертикальных линий для каждой кривой

        # Основные графики напряжений
        for i in range(stresses.shape[0]):  # Проходим по всем расчетным случаям
            line, = ax.step(
                self.X,  # Координаты X
                stresses[i],  # Значения напряжений для текущего расчетного случая
                where='post',  # Стиль линии ("ступеньки")
                label=self.LC_names[i]  # Метка для легенды
            )
            lines.append(line)  # Добавляем линию в список

            # Добавляем вертикальные линии с шагом 0.2
            x_min = np.min(self.X)  # Минимальное значение X
            x_max = np.max(self.X)  # Максимальное значение X
            x_ticks = np.arange(x_min, x_max, 0.2)  # Шаг 0.2
            v_lines = []  # Храним вертикальные линии для текущей кривой
            for x in x_ticks:
                idx = np.searchsorted(self.X, x, side='right') - 1  # Находим индекс ближайшего значения X
                idx = np.clip(idx, 0, len(self.X) - 1)  # Защита от выхода за границы массива
                stress_val = stresses[i, idx]  # Значение напряжения на кривой
                v_line, = ax.plot(
                    [x, x], [0, stress_val],  # Вертикальная линия от 0 до значения напряжения
                    color=line.get_color(),  # Цвет совпадает с цветом кривой
                    linestyle='--',          # Пунктирная линия
                    linewidth=0.5,           # Толщина линии
                    alpha=0.7                # Прозрачность
                )
                v_lines.append(v_line)  # Добавляем вертикальную линию в список
            vertical_lines.append(v_lines)  # Добавляем список вертикальных линий для текущей кривой

        # Критическое напряжение
        ax.axhline(
            y=sigma_cr,  # Значение критического напряжения
            color='r',  # Цвет линии (красный)
            linestyle='--',  # Пунктирная линия
            label=f'Критическое напряжение ({sigma_cr} МПа)'  # Метка для легенды
        )

        # Настройка осей графика
        ax.set_xlabel('Координата X')  # Подпись оси X
        ax.set_ylabel('Напряжение, МПа')  # Подпись оси Y
        ax.set_title('Эпюры напряжений для всех расчетных случаев')  # Заголовок графика
        ax.grid(True)  # Включаем сетку

        # Область для легенды справа
        ax_legend = fig.add_axes([0.75, 0.4, 0.2, 0.5])  # [left, bottom, width, height]
        ax_legend.axis('off')  # Отключаем оси в области легенды

        # Легенда
        legend_items = []  # Список для хранения элементов легенды
        visibility = [True] * len(lines)  # Все линии изначально видимы
        last_index = len(lines)  # Количество расчетных случаев
        for i, line in enumerate(lines):  # Проходим по всем линиям
            color = line.get_color()  # Получаем цвет линии
            # Короткая цветная линия
            line_patch = ax_legend.plot(
                [0.1, 0.2], [1 - (i + 1) / (last_index + 1), 1 - (i + 1) / (last_index + 1)],  # Позиция линии
                color=color,  # Цвет линии
                linewidth=2,  # Толщина линии
                transform=ax_legend.transAxes  # Используем относительные координаты
            )[0]
            # Текст черного цвета
            text = ax_legend.text(
                0.25, 1 - (i + 1) / (last_index + 1),  # Позиция текста
                line.get_label(),  # Текст метки
                color='black',  # Цвет текста
                fontsize=10,  # Размер шрифта
                transform=ax_legend.transAxes  # Используем относительные координаты
            )
            text.set_picker(True)  # Делаем текст кликабельным
            legend_items.append((line_patch, text))  # Добавляем элементы легенды в список

        # Подсказка
        tooltip = None  # Переменная для хранения подсказки

        def on_motion(event):
            nonlocal tooltip  # Используем переменную tooltip из внешней области видимости
            if event.inaxes == ax_legend:  # Если курсор над областью легенды
                if tooltip is None or not tooltip.get_visible():  # Если подсказка еще не отображается
                    # Создаем подсказку
                    tooltip = ax_legend.annotate(
                        "Управление видимостью по клику",  # Текст подсказки
                        xy=(0.5, 1.05),  # Позиция подсказки (в координатах аксиальной системы)
                        xycoords='axes fraction',  # Используем относительные координаты
                        ha='center',  # Горизонтальное выравнивание
                        va='bottom',  # Вертикальное выравнивание
                        fontsize=10,  # Размер шрифта
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='gray', alpha=0.8)  # Стиль фона
                    )
                    tooltip.set_visible(True)  # Делаем подсказку видимой
                    plt.draw()  # Перерисовываем график
            else:
                if tooltip is not None and tooltip.get_visible():  # Если подсказка отображается
                    # Убираем подсказку
                    tooltip.set_visible(False)  # Делаем подсказку невидимой
                    plt.draw()  # Перерисовываем график

        # Подключаем обработчик движения курсора
        fig.canvas.mpl_connect('motion_notify_event', on_motion)

        # Обработчик кликов по легенде
        def on_legend_click(event):
            for i, (line_patch, text) in enumerate(legend_items):  # Проходим по всем элементам легенды
                if event.artist == text:  # Если кликнули на текст
                    visibility[i] = not visibility[i]  # Переключаем состояние видимости
                    lines[i].set_visible(visibility[i])  # Обновляем видимость линии
                    for v_line in vertical_lines[i]:
                        v_line.set_visible(visibility[i])  # Обновляем видимость вертикальных линий
                    alpha = 0.2 if not visibility[i] else 1.0  # Устанавливаем прозрачность
                    line_patch.set_alpha(alpha)  # Полупрозрачность цветной линии
                    text.set_alpha(alpha)  # Полупрозрачность текста
                    plt.draw()  # Перерисовываем график
                    break

        # Подключаем обработчик кликов
        fig.canvas.mpl_connect('pick_event', on_legend_click)

        # Область для текста с минимальным КЗ
        ax_text = fig.add_axes([0.75, 0.1, 0.2, 0.2])  # [left, bottom, width, height]
        ax_text.axis('off')  # Отключаем оси

        # Добавляем информацию о минимальном КЗ
        min_results = self.find_min_ms(sigma_cr / stresses)  # Вычисляем минимальный коэффициент запаса
        min_value = min_results[0][0]  # Минимальное значение КЗ
        result_text = f"Минимальный КЗ:\n{min_value:.2f}\n\n"  # Формируем текст с минимальным КЗ
        result_text += "Случаи его появления:\n"
        for res in min_results:  # Добавляем информацию о случаях появления минимального КЗ
            result_text += f"Сечение {res[1]},  {res[2]}\n"

        # Текстовое поле с результатами
        text_obj = ax_text.text(
            0, 1,  # Позиция текста (верхний левый угол)
            result_text,  # Текст
            ha='left',  # Горизонтальное выравнивание
            va='top',   # Вертикальное выравнивание
            fontsize=12,  # Размер шрифта
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='black')  # Фон текста
        )

        plt.show()  # Отображаем график
  
# Чтение данных из Excel-файла
df = pd.read_excel('InputData.xlsx', sheet_name="Лист1", header=None)

# Извлечение необходимых данных
section_names = df.iloc[0, 2:].dropna().tolist()  # Названия сечений
X = df.iloc[1, 2:8].values.astype(float)  # Координаты X
A = df.iloc[3, 2:8].values.astype(float)  # Площади сечений

# Извлечение нагрузок
column_a = df[0]
filtered_indices = column_a[column_a.str.contains('Расчетный случай', na=False)].index
if not filtered_indices.empty:
    last_index = filtered_indices[-1]
else:
    last_index = None

loads = df.iloc[4:(last_index + 1), 2:8].values.astype(float)  # Нагрузки
LC_names = [f'LC{i + 1}' for i in range(last_index)]  # Названия расчетных случаев

# Создание объекта балки
beam = Beam(section_names, X, A, loads, LC_names)

# Расчет напряжений и коэффициентов запаса
sigma_cr = 500  # Критическое напряжение (МПа)
stresses = beam.calculate_stresses()
ms = beam.calculate_ms(sigma_cr, stresses)

# Визуализация результатов
beam.plot_stresses(stresses, sigma_cr)