from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent


def get_runtime_base_dir() -> Path:
    return PACKAGE_DIR


def package_path(relative_path: str | Path) -> Path:
    return PACKAGE_DIR / Path(relative_path)


def runtime_path(relative_path: str | Path) -> Path:
    return get_runtime_base_dir() / Path(relative_path)


def resolve_data_path(relative_path: str | Path) -> Path:
    return runtime_path(relative_path)


def resolve_version_file() -> Path:
    return runtime_path("version.json")
