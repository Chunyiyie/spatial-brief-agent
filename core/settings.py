import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

SECRETS_TOML_PATHS = (
    Path("/mount/.streamlit/secrets.toml"),
    Path("/.streamlit/secrets.toml"),
    Path(".streamlit/secrets.toml"),
)

_API_KEY_LINE_PATTERN = re.compile(
    r"^\s*(?:DEEPSEEK_API_KEY|DEEPSEEK-API-KEY|OPENAI_API_KEY)\s*=\s*"
    r'(?:"([^"]+)"|\'([^\']+)\'|(\S+))\s*$',
    re.IGNORECASE | re.MULTILINE,
)

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


def _collect_mapping_keys(root: Any, depth: int = 0) -> list[str]:
    if depth > 6:
        return []

    keys: list[str] = []
    mapping = _coerce_mapping(root)
    for key, value in mapping.items():
        keys.append(str(key))
        if isinstance(value, (dict, list)) or hasattr(value, "keys"):
            keys.extend(_collect_mapping_keys(value, depth + 1))
    return keys


def _load_toml_mapping(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore
        except ImportError:
            return None, "未安装 tomllib/tomli"

    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except Exception as exc:
        return None, f"TOML 解析失败: {exc}"

    if isinstance(data, dict):
        return data, ""
    return None, "TOML 根节点不是 table"


def _extract_api_key_from_text(text: str) -> str:
    for match in _API_KEY_LINE_PATTERN.finditer(text):
        for group in match.groups():
            if group:
                normalized = _normalize_secret_value(group)
                if normalized:
                    return normalized
    return ""


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
    for path in SECRETS_TOML_PATHS:
        if not path.is_file():
            continue

        data, _parse_error = _load_toml_mapping(path)
        if data is not None:
            for candidate in _collect_secret_candidates(data):
                normalized = _normalize_secret_value(candidate)
                if normalized:
                    return normalized

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        fallback = _extract_api_key_from_text(text)
        if fallback:
            return fallback

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

    toml_key = _read_secrets_from_toml_files()
    if toml_key:
        return toml_key

    streamlit_key = _read_from_streamlit_secrets()
    if streamlit_key:
        return streamlit_key

    return ""


def apply_streamlit_secrets_to_environ() -> None:
    api_key = get_deepseek_api_key()
    if api_key:
        os.environ[SECRET_KEY] = api_key


def describe_streamlit_secret_keys() -> str:
    return _describe_streamlit_secret_keys()


def _secrets_toml_exists() -> bool:
    return any(path.is_file() for path in SECRETS_TOML_PATHS)


def inspect_secrets_toml_files() -> list[dict[str, str]]:
    reports: list[dict[str, str]] = []

    for path in SECRETS_TOML_PATHS:
        if not path.is_file():
            continue

        size = path.stat().st_size
        data, parse_error = _load_toml_mapping(path)
        if data is not None:
            keys = _collect_mapping_keys(data)
            key_label = str(keys) if keys else "（文件可解析但没有任何键）"
        else:
            key_label = f"（{parse_error}）"

        try:
            text = path.read_text(encoding="utf-8")
            regex_hit = "是" if _extract_api_key_from_text(text) else "否"
        except Exception as exc:
            regex_hit = f"读文件失败: {exc}"

        reports.append(
            {
                "path": str(path),
                "size_bytes": str(size),
                "toml_keys": key_label,
                "regex_can_read_key": regex_hit,
            }
        )

    return reports


def deployment_key_diagnostics() -> dict[str, str]:
    api_key = get_deepseek_api_key()
    file_reports = inspect_secrets_toml_files()
    if file_reports:
        primary = file_reports[0]
        file_summary = (
            f"{primary['path']} size={primary['size_bytes']}B, "
            f"键={primary['toml_keys']}, 行匹配Key={primary['regex_can_read_key']}"
        )
    else:
        file_summary = "（未找到 secrets.toml 文件）"

    return {
        "api_key_loaded": "是" if api_key else "否",
        "env_DEEPSEEK_API_KEY": "已设置" if os.getenv(SECRET_KEY) else "未设置",
        "secrets_toml_on_disk": "是" if _secrets_toml_exists() else "否",
        "streamlit_secret_top_keys": describe_streamlit_secret_keys(),
        "secrets_toml_detail": file_summary,
    }


def missing_api_key_error_message() -> str:
    diag = deployment_key_diagnostics()
    hint = ""
    if diag["secrets_toml_on_disk"] == "是" and diag["api_key_loaded"] == "否":
        hint = (
            " 说明：Cloud 上常有空的 secrets.toml 占位文件；"
            "st.secrets 为空表示 Manage app → Secrets 里尚未成功 Save 或 TOML 无效。"
            "请只保留一行 DEEPSEEK_API_KEY = \"sk-...\"（英文引号），Save 后 Reboot。"
        )
    return (
        "未设置 DEEPSEEK_API_KEY。"
        " 本地请在 .env 中配置 DEEPSEEK_API_KEY；"
        " Streamlit Cloud 请在 Manage app → Settings → Secrets 填写："
        ' DEEPSEEK_API_KEY = "sk-..." 并 Reboot。'
        f" 诊断: api_key_loaded={diag['api_key_loaded']},"
        f" env={diag['env_DEEPSEEK_API_KEY']},"
        f" secrets.toml={diag['secrets_toml_on_disk']},"
        f" secrets 顶层键名={diag['streamlit_secret_top_keys']},"
        f" 文件详情={diag['secrets_toml_detail']}。"
        f"{hint}"
    )
