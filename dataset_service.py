"""Сервисный модуль обработки и реорганизации файловой структуры датасета.

Лабораторная работа №3 по курсу «Новые технологии в РПС».
Выполнил: студент Кондратенко А.С.
Содержит функции для создания файлов-аннотаций и копирования датасетов.
"""

from __future__ import annotations

from pathlib import Path
import random
import shutil
from typing import List, Tuple

import pandas as pd


def create_annotation_file(
    dataset_dir: Path | str,
    output_csv: Path | str,
) -> pd.DataFrame:
    """Создает CSV-файл аннотации для указанного каталога датасета.

    :param dataset_dir: Путь к каталогу с подпапками классов.
    :param output_csv: Путь к целевому файлу аннотации.
    :return: DataFrame с метаданными файлов.
    """
    root_path = Path(dataset_dir).resolve()
    project_root = Path.cwd().resolve()
    records: List[Tuple[str, str, str]] = []

    for class_folder in sorted(root_path.iterdir()):
        if not class_folder.is_dir():
            continue
        class_name = class_folder.name
        for file_path in sorted(class_folder.glob("*.txt")):
            abs_path = str(file_path.resolve())
            try:
                rel_path = str(file_path.relative_to(project_root))
            except ValueError:
                rel_path = str(file_path)
            records.append((abs_path, rel_path, class_name))

    columns = ["absolute_path", "relate_path", "output_class"]
    df = pd.DataFrame(data=records, columns=columns)

    out_file = Path(output_csv).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False, encoding="utf-8")
    return df


def copy_dataset_by_class(
    src_dir: Path | str,
    dst_dir: Path | str,
    output_csv: Path | str,
) -> pd.DataFrame:
    """Копирует датасет в единый каталог с именами <class>_<name>.txt.

    :param src_dir: Каталог исходного датасета.
    :param dst_dir: Каталог назначения.
    :param output_csv: Путь к файлу аннотации скопированного датасета.
    :return: DataFrame с обновленными метаданными.
    """
    source_path = Path(src_dir).resolve()
    target_path = Path(dst_dir).resolve()
    project_root = Path.cwd().resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    records: List[Tuple[str, str, str]] = []

    for class_folder in sorted(source_path.iterdir()):
        if not class_folder.is_dir():
            continue
        class_name = class_folder.name
        for src_file in sorted(class_folder.glob("*.txt")):
            dst_file = target_path / f"{class_name}_{src_file.name}"
            shutil.copy2(src_file, dst_file)
            abs_p = str(dst_file.resolve())
            try:
                rel_p = str(dst_file.relative_to(project_root))
            except ValueError:
                rel_p = str(dst_file)
            records.append((abs_p, rel_p, class_name))

    columns = ["absolute_path", "relate_path", "output_class"]
    df = pd.DataFrame(data=records, columns=columns)
    df.to_csv(Path(output_csv).resolve(), index=False, encoding="utf-8")
    return df


def copy_dataset_random_names(
    src_dir: Path | str,
    dst_dir: Path | str,
    output_csv: Path | str,
) -> pd.DataFrame:
    """Копирует файлы датасета со случайными номерами от 0 до 10000.

    :param src_dir: Исходный каталог датасета.
    :param dst_dir: Каталог назначения.
    :param output_csv: Путь к файлу аннотации.
    :return: DataFrame аннотации.
    """
    source_path = Path(src_dir).resolve()
    target_path = Path(dst_dir).resolve()
    project_root = Path.cwd().resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    files_with_classes: List[Tuple[Path, str]] = []
    for class_folder in sorted(source_path.iterdir()):
        if not class_folder.is_dir():
            continue
        for src_file in sorted(class_folder.glob("*.txt")):
            files_with_classes.append((src_file, class_folder.name))

    total = len(files_with_classes)
    if total == 0:
        return pd.DataFrame()

    random_numbers = random.sample(range(0, 10001), total)
    records: List[Tuple[str, str, str]] = []

    for (src_file, class_name), num in zip(files_with_classes, random_numbers):
        dst_file = target_path / f"{str(num).zfill(5)}.txt"
        shutil.copy2(src_file, dst_file)
        abs_p = str(dst_file.resolve())
        try:
            rel_p = str(dst_file.relative_to(project_root))
        except ValueError:
            rel_p = str(dst_file)
        records.append((abs_p, rel_p, class_name))

    columns = ["absolute_path", "relate_path", "output_class"]
    df = pd.DataFrame(data=records, columns=columns)
    df.to_csv(Path(output_csv).resolve(), index=False, encoding="utf-8")
    return df


if __name__ == "__main__":
    print("Самопроверка модуля dataset_service.py...")
    if Path("dataset").exists():
        test_df = create_annotation_file("dataset", "test_annotation.csv")
        print(f"Успешно создано строк аннотации: {len(test_df)}")
        Path("test_annotation.csv").unlink(missing_ok=True)
