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
    return {
        "version": version,
        "generated_at": generated_at,
        "file_names": [file_name],
        "files": {
            file_name: {
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        },
    }


@pytest.mark.asyncio
async def test_update_resource_does_not_write_version_when_full_download_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_dir = tmp_path / "runtime"
    monkeypatch.setenv(data_paths.DATA_DIR_ENV_VAR, str(runtime_dir))

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

    assert not (runtime_dir / "version.json").exists()


@pytest.mark.asyncio
async def test_update_resource_repairs_missing_files_when_version_matches(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    runtime_dir = tmp_path / "runtime"
    monkeypatch.setenv(data_paths.DATA_DIR_ENV_VAR, str(runtime_dir))

    file_name = "repair_me.json"
    expected_content = b'{"fixed": true}'
    remote_data = build_remote_data(file_name, expected_content)

    runtime_dir.mkdir(parents=True, exist_ok=True)
    with (runtime_dir / "version.json").open("w", encoding="utf-8") as f:
        json.dump(remote_data, f, ensure_ascii=False, indent=2)

    async def fake_fetch_json(session, url):
        del session, url
        return remote_data

    async def fake_fetch_file(session, url, save_path):
        del session, url
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(expected_content)

    monkeypatch.setattr(update, "fetch_json", fake_fetch_json)
    monkeypatch.setattr(update, "fetch_file", fake_fetch_file)

    message = await update.update_resource()

    assert message == "检测到本地数据文件缺失或损坏, 本次已更新1个文件"
    assert (runtime_dir / "excel" / file_name).read_bytes() == expected_content


def test_resolve_data_path_prefers_runtime_overlay(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    package_dir = tmp_path / "package"
    runtime_dir = tmp_path / "runtime"
    relative_path = Path("excel") / "example.json"

    package_file = package_dir / relative_path
    runtime_file = runtime_dir / relative_path

    package_file.parent.mkdir(parents=True, exist_ok=True)
    runtime_file.parent.mkdir(parents=True, exist_ok=True)
    package_file.write_text("package", encoding="utf-8")

    monkeypatch.setattr(data_paths, "PACKAGE_DIR", package_dir)
    monkeypatch.setenv(data_paths.DATA_DIR_ENV_VAR, str(runtime_dir))

    assert data_paths.resolve_data_path(relative_path) == package_file

    runtime_file.write_text("runtime", encoding="utf-8")

    assert data_paths.resolve_data_path(relative_path) == runtime_file
