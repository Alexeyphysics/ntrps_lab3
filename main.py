"""Точка входа для запуска GUI-приложения ЛР3.

Лабораторная работа №3 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С.
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from main_window import MainWindow


def main() -> None:
    """Инициализация приложения и запуск цикла обработки событий Qt."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
