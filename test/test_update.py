# ruff: noqa: S101

import hashlib
import json
from pathlib import Path

import pytest

from starrail_damage_cal import data_paths, update


def build_remote_data(
    file_name: str,
    content: bytes,
    *,
    version: str = "9.9.9",
    generated_at: str = "2026-03-25T00:00:00Z",
) -> dict:
    return build_remote_data_for_files(
        {file_name: content},
        version=version,
        generated_at=generated_at,
    )


def build_remote_data_for_files(
    files: dict[str, bytes],
    *,
    version: str = "9.9.9",
    generated_at: str = "2026-03-25T00:00:00Z",
) -> dict:
    return {
        "version": version,
        "generated_at": generated_at,
        "file_names": list(files),
        "files": {
            file_name: {
                "sha256": hashlib.sha256(content).hexdigest(),
            }
            for file_name, content in files.items()
        },
    }


@pytest.mark.asyncio
async def test_update_resource_does_not_write_version_when_full_download_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    package_dir = tmp_path / "package"
    monkeypatch.setattr(data_paths, "PACKAGE_DIR", package_dir)

    remote_data = build_remote_data("broken.json", b"{}")

    async def fake_fetch_json(session, url):
        del session, url
        return remote_data

    async def failing_download(session, version_data):
        del session, version_data
        msg = "download failed"
        raise RuntimeError(msg)

    monkeypatch.setattr(update, "fetch_json", fake_fetch_json)
    monkeypatch.setattr(update, "download_all_files", failing_download)

    with pytest.raises(RuntimeError, match="download failed"):
        await update.update_resource()

    assert not (package_dir / "version.json").exists()


@pytest.mark.asyncio
async def test_update_resource_repairs_missing_files_when_version_matches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    package_dir = tmp_path / "package"
    monkeypatch.setattr(data_paths, "PACKAGE_DIR", package_dir)

    repaired_file_name = "repair_me.json"
    unchanged_file_name = "already_ok.json"
    expected_files = {
        repaired_file_name: b'{"fixed": true}',
        unchanged_file_name: b'{"already": true}',
    }
    remote_data = build_remote_data_for_files(expected_files)

    package_dir.mkdir(parents=True, exist_ok=True)
    with (package_dir / "version.json").open("w", encoding="utf-8") as f:
        json.dump(remote_data, f, ensure_ascii=False, indent=2)
    unchanged_file = package_dir / "excel" / unchanged_file_name
    unchanged_file.parent.mkdir(parents=True, exist_ok=True)
    unchanged_file.write_bytes(expected_files[unchanged_file_name])

    downloaded_files = []
    async def fake_fetch_json(session, url):
        del session, url
        return remote_data

    async def fake_fetch_file(session, url, save_path):
        del session, url
        downloaded_files.append(save_path.name)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(expected_files[save_path.name])

    monkeypatch.setattr(update, "fetch_json", fake_fetch_json)
    monkeypatch.setattr(update, "fetch_file", fake_fetch_file)
    monkeypatch.setattr(update, "refresh_loaded_data", lambda: None)

    message = await update.update_resource()

    assert message == "检测到本地数据文件缺失或损坏, 本次已更新2个文件"
    assert set(downloaded_files) == {repaired_file_name, unchanged_file_name}
    assert (
        package_dir / "excel" / repaired_file_name
    ).read_bytes() == expected_files[repaired_file_name]
    assert unchanged_file.read_bytes() == expected_files[unchanged_file_name]


def test_data_paths_use_package_location_and_ignore_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    package_dir = tmp_path / "package"
    environment_dir = tmp_path / "environment"
    relative_path = Path("excel") / "example.json"

    monkeypatch.setattr(data_paths, "PACKAGE_DIR", package_dir)
    monkeypatch.setenv("STARRAIL_DAMAGE_CAL_DATA_DIR", str(environment_dir))

    assert data_paths.get_runtime_base_dir() == package_dir
    assert data_paths.runtime_path(relative_path) == package_dir / relative_path
    assert data_paths.resolve_data_path(relative_path) == package_dir / relative_path
    assert data_paths.resolve_version_file() == package_dir / "version.json"


def test_cleanup_stale_runtime_files_preserves_local_required_mapping(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    package_dir = tmp_path / "package"
    monkeypatch.setattr(data_paths, "PACKAGE_DIR", package_dir)

    retained_file = (
        package_dir / "map" / "data" / "MysPropertyType2Property_mapping.json"
    )
    stale_file = package_dir / "map" / "data" / "stale_mapping.json"
    managed_file = package_dir / "map" / "data" / "avatarId2Name_mapping.json"

    retained_file.parent.mkdir(parents=True, exist_ok=True)
    retained_file.write_text("{}", encoding="utf-8")
    stale_file.write_text("{}", encoding="utf-8")
    managed_file.write_text("{}", encoding="utf-8")

    remote_data = build_remote_data("avatarId2Name_mapping.json", b"{}")

    update.cleanup_stale_runtime_files(remote_data)

    assert retained_file.exists()
    assert managed_file.exists()
    assert not stale_file.exists()
