import os
from typing import Any

from dotenv import load_dotenv

SECRET_KEY = "DEEPSEEK_API_KEY"

_NESTED_SECRET_SECTIONS = (
    "secrets",
    "default",
    "general",
    "streamlit",
    "deepseek",
)


def _normalize_secret_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().strip('"').strip("'")


def _read_from_streamlit_secrets() -> str:
    try:
        import streamlit as st
    except ImportError:
        return ""

    try:
        secrets = st.secrets
    except Exception:
        return ""

    candidates: list[Any] = []

    if SECRET_KEY in secrets:
        candidates.append(secrets[SECRET_KEY])

    try:
        attr_value = getattr(secrets, SECRET_KEY, None)
        if attr_value is not None:
            candidates.append(attr_value)
    except Exception:
        pass

    for section in _NESTED_SECRET_SECTIONS:
        if section not in secrets:
            continue

        block = secrets[section]
        try:
            if isinstance(block, dict):
                if SECRET_KEY in block:
                    candidates.append(block[SECRET_KEY])
            elif SECRET_KEY in block:
                candidates.append(block[SECRET_KEY])
            else:
                nested = getattr(block, SECRET_KEY, None)
                if nested is not None:
                    candidates.append(nested)
        except Exception:
            continue

    for candidate in candidates:
        normalized = _normalize_secret_value(candidate)
        if normalized:
            return normalized

    return ""


def get_deepseek_api_key() -> str:
    load_dotenv()

    env_key = _normalize_secret_value(os.getenv(SECRET_KEY))
    if env_key:
        return env_key

    return _read_from_streamlit_secrets()


def apply_streamlit_secrets_to_environ() -> None:
    api_key = _read_from_streamlit_secrets()
    if api_key:
        os.environ[SECRET_KEY] = api_key
        