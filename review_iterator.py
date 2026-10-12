"""Модуль итерации и чтения отзывов для интеграции с GUI.

Лабораторная работа №3 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С.
Содержит класс ReviewIterator для последовательного чтения отзывов.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator, List, Tuple


def read_review_file(file_path: Path | str) -> Tuple[str, str]:
    """Считывает заголовок и текст из файла отзыва.

    :param file_path: Путь к текстовому файлу отзыва.
    :return: Кортеж вида (заголовок, текст_отзыва).
    """
    path = Path(file_path)
    if not path.exists():
        return ("Ошибка", f"Файл не найден: {path}")

    try:
        content = path.read_text(encoding="utf-8").strip()
        lines = content.split("\n", 1)
        title = lines[0].strip() if lines else "Без заголовка"
        body = lines[1].strip() if len(lines) > 1 else ""
        return (title, body)
    except OSError as err:
        return ("Ошибка чтения", str(err))


class ReviewIterator(Iterator[Tuple[str, str, str]]):
    """Итератор по отзывам заданного класса рейтинга."""

    def __init__(
        self,
        dataset_dir: Path | str,
        class_label: str | int,
    ) -> None:
        """Инициализация итератора для определенной оценки.

        :param dataset_dir: Путь к корневому каталогу датасета.
        :param class_label: Метка класса (например, '1', '5').
        """
        self.dataset_dir = Path(dataset_dir)
        self.class_label = str(class_label)
        self.files: List[Path] = self._load_file_list()
        self.cursor: int = 0

    def _load_file_list(self) -> List[Path]:
        """Находит все текстовые файлы в подкаталоге класса."""
        class_folder = self.dataset_dir / self.class_label
        if not class_folder.exists() or not class_folder.is_dir():
            return []
        return sorted(list(class_folder.glob("*.txt")))

    def reset(self) -> None:
        """Сбрасывает указатель итератора на начало списка."""
        self.cursor = 0

    def __iter__(self) -> ReviewIterator:
        """Возвращает сам экземпляр итератора."""
        return self

    def __next__(self) -> Tuple[str, str, str]:
        """Возвращает кортеж (путь_к_файлу, заголовок, текст_отзыва).

        Выбрасывает StopIteration по окончании файлов.
        """
        if self.cursor >= len(self.files):
            raise StopIteration

        file_path = self.files[self.cursor]
        self.cursor += 1
        title, body = read_review_file(file_path)
        return (str(file_path.resolve()), title, body)

    def __len__(self) -> int:
        """Возвращает общее количество доступных файлов."""
        return len(self.files)


if __name__ == "__main__":
    print("Самопроверка модуля review_iterator.py...")
    if Path("dataset").exists():
        test_iter = ReviewIterator("dataset", "1")
        print(f"Найдено отзывов класса '1': {len(test_iter)}")
        if len(test_iter) > 0:
            first_path, f_title, f_body = next(test_iter)
            print(f"Первый отзыв: {f_title} ({first_path})")
