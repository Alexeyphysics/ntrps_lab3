"""Модуль графического интерфейса пользователя (PySide6 / Qt6).

Лабораторная работа №3 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С.
Реализует главное окно десктопного приложения без алгоритмической логики.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Dict


from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from dataset_service import (
    copy_dataset_by_class,
    copy_dataset_random_names,
    create_annotation_file,
)
from review_iterator import ReviewIterator


class MainWindow(QMainWindow):
    """Главное окно приложения для управления и анализа датасета отзывов."""

    def __init__(self) -> None:
        """Инициализация окна и привязка элементов управления."""
        super().__init__()
        self.setWindowTitle(
            "Анализатор датасета отзывов - ЛР3 (Кондратенко А.С.)"
        )
        self.setMinimumSize(850, 700)

        # Текущий рабочий каталог датасета
        default_dir = Path("dataset").resolve()
        self.current_dataset_dir: Path = (
            default_dir if default_dir.exists() else Path.cwd()
        )

        # Реестр итераторов для классов оценок 1-5
        self.iterators: Dict[str, ReviewIterator] = {}
        self._init_iterators()

        self._init_ui()

    def _init_iterators(self) -> None:
        """Инициализирует или перезапускает итераторы для всех классов."""
        self.iterators = {
            str(star): ReviewIterator(self.current_dataset_dir, str(star))
            for star in range(1, 6)
        }

    def _init_ui(self) -> None:
        """Компоновка графических элементов интерфейса."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # Блок 1: Выбор папки датасета
        main_layout.addWidget(self._create_folder_select_group())

        # Блок 2: Создание аннотаций и реорганизация датасетов
        main_layout.addWidget(self._create_operations_group())

        # Блок 3: Интерактивный просмотр отзывов по классам (Итераторы)
        main_layout.addWidget(self._create_viewer_group())

    def _create_folder_select_group(self) -> QGroupBox:
        """Создает группу выбора исходного каталога датасета."""
        group = QGroupBox("1. Каталог исходного датасета")
        layout = QHBoxLayout(group)

        self.path_display = QLineEdit(str(self.current_dataset_dir))
        self.path_display.setReadOnly(True)
        layout.addWidget(self.path_display)

        select_btn = QPushButton("Выбрать папку...")
        select_btn.clicked.connect(self._select_dataset_folder)
        layout.addWidget(select_btn)

        return group

    def _create_operations_group(self) -> QGroupBox:
        """Создает группу операций с файлами и аннотациями (ЛР2)."""
        group = QGroupBox("2. Создание аннотаций и реорганизация файлов")
        layout = QVBoxLayout(group)

        # Кнопка аннотации исходного датасета
        btn_annot = QPushButton("Создать аннотацию исходного датасета (CSV)")
        btn_annot.clicked.connect(self._create_source_annotation)
        layout.addWidget(btn_annot)

        # Кнопка копирования с префиксом класса
        btn_class_copy = QPushButton(
            "Создать копию датасета с именами вида <класс>_<номер>.txt"
        )
        btn_class_copy.clicked.connect(self._create_class_copy)
        layout.addWidget(btn_class_copy)

        # Кнопка копирования со случайными номерами
        btn_rand_copy = QPushButton(
            "Создать копию датасета со случайными номерами (0..10000)"
        )
        btn_rand_copy.clicked.connect(self._create_random_copy)
        layout.addWidget(btn_rand_copy)

        return group

    def _create_viewer_group(self) -> QGroupBox:
        """Создает группу просмотра отзывов с помощью итераторов."""
        group = QGroupBox(
            "3. Просмотр отзывов по классам рейтинга (Итераторы)"
        )
        layout = QVBoxLayout(group)

        # Панель кнопок для каждого класса (1–5 звезд)
        btn_panel = QHBoxLayout()
        for star in range(1, 6):
            btn = QPushButton(f"Следующий: ★ {star}")
            # Замыкание переменной star через параметр по умолчанию
            btn.clicked.connect(
                lambda checked=False, s=str(star): self._show_next_review(s)
            )
            btn_panel.addWidget(btn)
        layout.addLayout(btn_panel)

        # Метаданные текущего открытого отзыва
        self.info_label = QLabel("Файл не выбран")
        self.info_label.setStyleSheet("font-weight: bold; color: #2980b9;")
        layout.addWidget(self.info_label)

        # Поле для отображения полного текста отзыва
        self.review_text_area = QTextEdit()
        self.review_text_area.setReadOnly(True)
        self.review_text_area.setPlaceholderText(
            "Здесь будет отображен текст выбранного отзыва..."
        )
        layout.addWidget(self.review_text_area)

        return group

    def _select_dataset_folder(self) -> None:
        """Открывает диалог выбора каталога датасета."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку исходного датасета",
            str(self.current_dataset_dir),
        )
        if folder:
            self.current_dataset_dir = Path(folder).resolve()
            self.path_display.setText(str(self.current_dataset_dir))
            self._init_iterators()
            QMessageBox.information(
                self,
                "Каталог обновлен",
                f"Выбран каталог:\n{self.current_dataset_dir}",
            )

    def _create_source_annotation(self) -> None:
        """Запрашивает путь и сохраняет аннотацию исходного датасета."""
        csv_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить аннотацию исходного датасета",
            "annotation_gui.csv",
            "CSV Files (*.csv)",
        )
        if not csv_path:
            return

        df = create_annotation_file(self.current_dataset_dir, csv_path)
        QMessageBox.information(
            self,
            "Успех",
            f"Файл-аннотация успешно создан!\nЗаписей: {len(df)}\nПуть: {csv_path}",
        )

    def _create_class_copy(self) -> None:
        """Создает копию датасета с именами <класс>_<номер>.txt."""
        target_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку назначения для копии (класс_номер)",
        )
        if not target_dir:
            return

        annot_path = Path(target_dir) / "annotation_class.csv"
        df = copy_dataset_by_class(
            self.current_dataset_dir, target_dir, annot_path
        )
        QMessageBox.information(
            self,
            "Успех",
            f"Скопировано файлов: {len(df)}\n"
            f"Папка: {target_dir}\n"
            f"Аннотация: {annot_path}",
        )

    def _create_random_copy(self) -> None:
        """Создает копию датасета со случайными номерами."""
        target_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку назначения для случайных номеров",
        )
        if not target_dir:
            return

        annot_path = Path(target_dir) / "annotation_random.csv"
        df = copy_dataset_random_names(
            self.current_dataset_dir, target_dir, annot_path
        )
        QMessageBox.information(
            self,
            "Успех",
            f"Скопировано файлов: {len(df)}\n"
            f"Папка: {target_dir}\n"
            f"Аннотация: {annot_path}",
        )

    def _show_next_review(self, class_label: str) -> None:
        """Извлекает и отображает следующий отзыв выбранного класса."""
        iterator = self.iterators.get(class_label)
        if iterator is None:
            return

        try:
            file_path, title, body = next(iterator)
            idx = iterator.cursor
            total = len(iterator)
            self.info_label.setText(
                f"Класс ★ {class_label} | Отзыв {idx}/{total} | Файл: {Path(file_path).name}"
            )
            full_content = f"ЗАГОЛОВОК:\n{title}\n\nТЕКСТ ОТЗЫВА:\n{body}"
            self.review_text_area.setPlainText(full_content)
        except StopIteration:
            QMessageBox.information(
                self,
                "Просмотр завершен",
                f"Все отзывы класса ★ {class_label} исчерпаны!\n"
                "Счетчик сброшен в начало.",
            )
            iterator.reset()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
