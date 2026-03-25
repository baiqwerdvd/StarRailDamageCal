import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_DIR_ENV_VAR = "STARRAIL_DAMAGE_CAL_DATA_DIR"
DEFAULT_RUNTIME_DIR_NAME = ".starrail_damage_cal"


def get_runtime_base_dir() -> Path:
    custom_dir = os.getenv(DATA_DIR_ENV_VAR)
    if custom_dir:
        return Path(custom_dir).expanduser().resolve()
    return Path.home() / DEFAULT_RUNTIME_DIR_NAME


def package_path(relative_path: str | Path) -> Path:
    return PACKAGE_DIR / Path(relative_path)


def runtime_path(relative_path: str | Path) -> Path:
    return get_runtime_base_dir() / Path(relative_path)


def resolve_data_path(relative_path: str | Path) -> Path:
    runtime_file = runtime_path(relative_path)
    if runtime_file.exists():
        return runtime_file
    return package_path(relative_path)


def resolve_version_file() -> Path:
    runtime_version = runtime_path("version.json")
    if runtime_version.exists():
        return runtime_version
    return package_path("version.json")
