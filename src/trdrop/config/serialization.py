"""YAML serialization for configuration types.

Provides conversion between config dataclasses and YAML-compatible dicts.
"""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar, get_args, get_origin, get_type_hints

import yaml

from trdrop.config.types import (
    GlobalRef,
    Position,
    PresetConfig,
    Reference,
    Size,
    VideoRef,
)

T = TypeVar("T")


# =============================================================================
# Reference Serialization
# =============================================================================


def reference_to_str(ref: Reference) -> str:
    """Convert Reference to YAML string."""
    match ref:
        case GlobalRef():
            return "global"
        case VideoRef(index=idx):
            return f"video:{idx}"


def reference_from_str(s: str) -> Reference:
    """Parse YAML string to Reference."""
    if s == "global":
        return GlobalRef()
    if s.startswith("video:"):
        idx = int(s.split(":")[1])
        return VideoRef(idx)
    raise ValueError(f"Invalid reference: {s}")


# =============================================================================
# Generic Serialization Helpers
# =============================================================================


def _enum_to_str(e: Enum) -> str:
    """Convert enum to its value string."""
    return e.value


def _str_to_enum(s: str, enum_type: type[Enum]) -> Enum:
    """Convert string to enum value."""
    return enum_type(s)


def _is_optional(field_type: type) -> bool:
    """Check if a type is Optional[T]."""
    origin = get_origin(field_type)
    if origin is not type(None | int):  # UnionType
        return False
    args = get_args(field_type)
    return type(None) in args


def _get_optional_inner(field_type: type) -> type:
    """Get the T from Optional[T]."""
    args = get_args(field_type)
    for arg in args:
        if arg is not type(None):
            return arg
    raise ValueError(f"Could not extract inner type from {field_type}")


# =============================================================================
# To Dict (for YAML serialization)
# =============================================================================


def position_to_dict(pos: Position) -> dict[str, Any]:
    """Serialize Position to dict."""
    return {
        "x": pos.x,
        "y": pos.y,
        "ref": reference_to_str(pos.ref),
    }


def size_to_dict(size: Size) -> dict[str, Any]:
    """Serialize Size to dict."""
    return {
        "width": size.width,
        "height": size.height,
        "ref": reference_to_str(size.ref),
    }


def _value_to_dict(value: Any) -> Any:
    """Convert a value to YAML-serializable form."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Position):
        return position_to_dict(value)
    if isinstance(value, Size):
        return size_to_dict(value)
    if isinstance(value, Enum):
        return _enum_to_str(value)
    if isinstance(value, (list, tuple)):
        return [_value_to_dict(v) for v in value]
    if isinstance(value, dict):
        return {k: _value_to_dict(v) for k, v in value.items()}
    if is_dataclass(value) and not isinstance(value, type):
        return dataclass_to_dict(value)
    return value


def dataclass_to_dict(obj: Any) -> dict[str, Any]:
    """Convert a dataclass to a dict for YAML serialization."""
    if not is_dataclass(obj):
        raise TypeError(f"Expected dataclass, got {type(obj)}")

    result: dict[str, Any] = {}
    for f in fields(obj):
        value = getattr(obj, f.name)
        result[f.name] = _value_to_dict(value)

    return result


# =============================================================================
# From Dict (for YAML deserialization)
# =============================================================================


def position_from_dict(d: dict[str, Any]) -> Position:
    """Deserialize Position from dict."""
    return Position(
        x=d["x"],
        y=d["y"],
        ref=reference_from_str(d["ref"]),
    )


def size_from_dict(d: dict[str, Any]) -> Size:
    """Deserialize Size from dict."""
    return Size(
        width=d["width"],
        height=d["height"],
        ref=reference_from_str(d["ref"]),
    )


def _dict_to_value(data: Any, target_type: Any) -> Any:
    """Convert YAML data to a typed value."""
    if data is None:
        return None

    # Handle Optional types
    if _is_optional(target_type):
        if data is None:
            return None
        target_type = _get_optional_inner(target_type)

    # Handle basic types
    if target_type in (str, int, float, bool):
        return target_type(data)

    # Handle Position
    if target_type is Position:
        return position_from_dict(data)

    # Handle Size
    if target_type is Size:
        return size_from_dict(data)

    # Handle enums
    if isinstance(target_type, type) and issubclass(target_type, Enum):
        return _str_to_enum(data, target_type)

    # Handle tuples
    origin = get_origin(target_type)
    if origin is tuple:
        args = get_args(target_type)
        if args and args[-1] is ...:
            # Variable length tuple like tuple[int, ...]
            elem_type = args[0]
            return tuple(_dict_to_value(v, elem_type) for v in data)
        else:
            # Fixed length tuple
            return tuple(_dict_to_value(v, t) for v, t in zip(data, args))

    # Handle lists
    if origin is list:
        elem_type = get_args(target_type)[0]
        return [_dict_to_value(v, elem_type) for v in data]

    # Handle dicts
    if origin is dict:
        key_type, val_type = get_args(target_type)
        return {
            _dict_to_value(k, key_type): _dict_to_value(v, val_type)
            for k, v in data.items()
        }

    # Handle dataclasses
    if is_dataclass(target_type) and isinstance(target_type, type):
        return dict_to_dataclass(data, target_type)

    # Fallback
    return data


def dict_to_dataclass(data: dict[str, Any], cls: type[T]) -> T:
    """Convert a dict to a dataclass instance."""
    if not is_dataclass(cls):
        raise TypeError(f"Expected dataclass type, got {cls}")

    # Resolve type hints (handles forward references from __future__ annotations)
    try:
        type_hints = get_type_hints(cls)
    except Exception:
        # Fallback to field.type if get_type_hints fails
        type_hints = {f.name: f.type for f in fields(cls)}

    kwargs: dict[str, Any] = {}
    for f in fields(cls):
        if f.name in data:
            field_type = type_hints.get(f.name, f.type)
            kwargs[f.name] = _dict_to_value(data[f.name], field_type)
        # Missing fields use defaults

    return cls(**kwargs)


# =============================================================================
# YAML File I/O
# =============================================================================


def preset_to_yaml(config: PresetConfig) -> str:
    """Serialize PresetConfig to YAML string."""
    data = dataclass_to_dict(config)
    return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)


def preset_from_yaml(yaml_str: str) -> PresetConfig:
    """Deserialize PresetConfig from YAML string."""
    data = yaml.safe_load(yaml_str)
    if data is None:
        return PresetConfig()
    return dict_to_dataclass(data, PresetConfig)


def save_preset(config: PresetConfig, path: Path | str) -> None:
    """Save PresetConfig to a YAML file."""
    path = Path(path)
    yaml_str = preset_to_yaml(config)
    path.write_text(yaml_str, encoding="utf-8")


def load_preset(path: Path | str) -> PresetConfig:
    """Load PresetConfig from a YAML file."""
    path = Path(path)
    yaml_str = path.read_text(encoding="utf-8")
    return preset_from_yaml(yaml_str)
