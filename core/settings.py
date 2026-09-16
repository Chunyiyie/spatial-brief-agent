import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

SECRET_KEY = "DEEPSEEK_API_KEY"
SECRET_ALIASES = {
    "DEEPSEEK_API_KEY",
    "DEEPSEEK-API-KEY",
    "OPENAI_API_KEY",
}


def _normalize_secret_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().strip('"').strip("'")


def _is_target_secret_name(name: str) -> bool:
    normalized = name.upper().replace("-", "_")
    return normalized in SECRET_ALIASES


def _coerce_mapping(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj

    try:
        return dict(obj)
    except Exception:
        pass

    try:
        return {key: obj[key] for key in obj.keys()}
    except Exception:
        return {}


def _collect_secret_candidates(root: Any, depth: int = 0) -> list[Any]:
    if depth > 6:
        return []

    candidates: list[Any] = []

    if isinstance(root, (str, int, float)):
        candidates.append(root)
        return candidates

    mapping = _coerce_mapping(root)
    for key, value in mapping.items():
        if _is_target_secret_name(str(key)):
            candidates.append(value)

        if isinstance(value, (dict, list)) or hasattr(value, "keys"):
            candidates.extend(_collect_secret_candidates(value, depth + 1))
        elif _is_target_secret_name(str(key)):
            candidates.append(value)

    return candidates


def _read_secrets_from_toml_files() -> str:
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            return ""

    candidate_paths = [
        Path("/mount/.streamlit/secrets.toml"),
        Path("/.streamlit/secrets.toml"),
        Path(".streamlit/secrets.toml"),
    ]

    for path in candidate_paths:
        if not path.is_file():
            continue

        try:
            with path.open("rb") as file:
                data = tomllib.load(file)
        except Exception:
            continue

        for candidate in _collect_secret_candidates(data):
            normalized = _normalize_secret_value(candidate)
            if normalized:
                return normalized

    return ""


def _read_from_streamlit_secrets() -> str:
    try:
        import streamlit as st
    except ImportError:
        return ""

    try:
        secrets = st.secrets
    except Exception:
        return ""

    candidates = _collect_secret_candidates(secrets)

    try:
        secrets_dict = secrets.to_dict()
        candidates.extend(_collect_secret_candidates(secrets_dict))
    except Exception:
        pass

    for candidate in candidates:
        normalized = _normalize_secret_value(candidate)
        if normalized:
            return normalized

    return ""


def _describe_streamlit_secret_keys() -> str:
    try:
        import streamlit as st
    except ImportError:
        return "（非 Streamlit 环境）"

    try:
        keys = list(st.secrets.keys())
        if not keys:
            return "（空，说明 Cloud Secrets 未生效）"
        return str(keys)
    except Exception as exc:
        return f"（读取失败: {exc}）"


def get_deepseek_api_key() -> str:
    load_dotenv()

    env_key = _normalize_secret_value(os.getenv(SECRET_KEY))
    if env_key:
        return env_key

    streamlit_key = _read_from_streamlit_secrets()
    if streamlit_key:
        return streamlit_key

    return _read_secrets_from_toml_files()


def apply_streamlit_secrets_to_environ() -> None:
    api_key = get_deepseek_api_key()
    if api_key:
        os.environ[SECRET_KEY] = api_key


def missing_api_key_error_message() -> str:
    return (
        "未设置 DEEPSEEK_API_KEY。"
        " 本地请在 .env 中配置 DEEPSEEK_API_KEY；"
        " Streamlit Cloud 请在 Manage app → Settings → Secrets 填写："
        ' DEEPSEEK_API_KEY = "sk-..." 并 Reboot。'
        f" 当前 Streamlit secrets 顶层键名: {_describe_streamlit_secret_keys()}"
    )
