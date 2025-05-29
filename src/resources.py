"""Resources."""

from pathlib import Path

from src import config


def _read_file(filename: str) -> str:
    dst = Path(config.RESOURCES_FOLDER)
    filepath = dst / filename
    with open(filepath, encoding='utf-8') as file:
        return file.read().strip()


json_example_minified_1 = _read_file('example1.minified.json')
json_example_minified_2 = _read_file('example2.minified.json')
json_schema_minified = _read_file('schema.minified.json')
