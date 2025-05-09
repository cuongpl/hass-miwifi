"""Handle MiWiFi Frontend panel."""

import os
import json
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.components.frontend import async_register_built_in_panel, async_remove_panel

from .const import (
    PANEL_REPO_VERSION_URL,
    PANEL_REPO_FILES_URL,
    PANEL_REPO_BASE_URL,
    PANEL_LOCAL_PATH,
    PANEL_STORAGE_FILE,
)
from .logger import _LOGGER


async def async_download_panel_if_needed(hass: HomeAssistant) -> str:
    """Check and download panel if needed. Return the version."""
    async with aiohttp.ClientSession() as session:
        try:
            remote_version = await read_remote_version(session)
            local_version = await read_local_version(hass)

            if remote_version != local_version:
                _LOGGER.info(f"[MiWiFi] Nueva versión del panel detectada: {remote_version}, actualizando archivos...")
                await download_panel_files(hass, session, remote_version)
                await save_local_version(hass, remote_version)
            else:
                _LOGGER.info(f"[MiWiFi] Versión {remote_version} detectada, comprobando archivos...")
                await download_panel_files(hass, session, remote_version)

            return remote_version

        except Exception as e:
            _LOGGER.error(f"[MiWiFi] Error al verificar/descargar el panel frontend: {e}")
            return "0.0"


async def read_remote_version(session: aiohttp.ClientSession) -> str:
    async with session.get(PANEL_REPO_VERSION_URL) as resp:
        resp.raise_for_status()
        text = await resp.text()
        data = json.loads(text)
        return data.get("version", "0.0")



async def read_remote_files(session: aiohttp.ClientSession) -> list:
    async with session.get(PANEL_REPO_FILES_URL) as resp:
        resp.raise_for_status()
        text = await resp.text()
        data = json.loads(text)
        return data.get("files", [])


async def read_local_version(hass: HomeAssistant) -> str:
    path = hass.config.path(PANEL_STORAGE_FILE)
    if not os.path.exists(path):
        return "0.0"
    return await hass.async_add_executor_job(_read_json_file, path)


def _read_json_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("version", "0.0")


async def save_local_version(hass: HomeAssistant, version: str) -> None:
    path = hass.config.path(PANEL_STORAGE_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    await hass.async_add_executor_job(_write_json_file, path, {"version": version})


def _write_json_file(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


async def download_panel_files(hass: HomeAssistant, session: aiohttp.ClientSession, remote_version: str) -> None:
    try:
        files = await read_remote_files(session)
    except Exception as e:
        _LOGGER.error(f"[MiWiFi] Error al leer files.json: {e}")
        return

    for file in files:
        remote_url = f"{PANEL_REPO_BASE_URL}{file}"
        local_path = hass.config.path(PANEL_LOCAL_PATH, file)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        async with session.get(remote_url) as resp:
            if resp.status != 200:
                _LOGGER.warning(f"[MiWiFi] No se pudo descargar {file} (status {resp.status})")
                continue

            remote_content = await resp.read()

            if file.endswith(".js"):
                content = remote_content.decode("utf-8").replace("__MIWIFI_VERSION__", remote_version)
                remote_content = content.encode("utf-8")

            if os.path.exists(local_path):
                existing_content = await hass.async_add_executor_job(_read_binary_file, local_path)
                if remote_content == existing_content:
                    continue

            await hass.async_add_executor_job(_write_binary_file, local_path, remote_content)
            _LOGGER.info(f"[MiWiFi] Archivo actualizado: {file}")


def _read_binary_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _write_binary_file(path: str, content: bytes) -> None:
    with open(path, "wb") as f:
        f.write(content)


async def async_register_panel(hass: HomeAssistant, version: str) -> None:
    """Register the MiWiFi panel in Home Assistant."""
    try:
        await async_remove_panel(hass, "miwifi")
    except Exception:
        pass

    async_register_built_in_panel(
        hass,
        component_name="custom",
        sidebar_title="MiWiFi",
        sidebar_icon="mdi:router-network",
        frontend_url_path="miwifi",
        config={
            "_panel_custom": {
                "name": "miwifi-panel",
                "module_url": f"/local/miwifi/panel-frontend.js?v={version}",
                "embed_iframe": False,
                "trust_external_script": False,
            }
        },
        require_admin=True,
    )
    _LOGGER.info("[MiWiFi] Panel registrado con éxito.")


async def async_remove_miwifi_panel(hass: HomeAssistant) -> None:
    try:
        await async_remove_panel(hass, "miwifi")
        _LOGGER.info("[MiWiFi] Panel eliminado correctamente.")
    except Exception as e:
        _LOGGER.debug(f"[MiWiFi] El panel no estaba registrado: {e}")
