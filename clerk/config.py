from dataclasses import dataclass
import yaml


@dataclass
class Config:
    doctrine: list
    refs: list
    channels: dict
    classification: dict
    dormant_days: int
    field_log_len: int
    user: str


def load_config(path: str) -> Config:
    with open(path, encoding="utf-8") as fh:
        d = yaml.safe_load(fh)
    clerk = d.get("clerk", {})
    return Config(
        doctrine=d["doctrine"],
        refs=d["refs"],
        channels=d.get("channels", {}),
        classification=d["classification"],
        dormant_days=int(clerk.get("dormant_days", 30)),
        field_log_len=int(clerk.get("field_log_len", 5)),
        user=d.get("user", "dharmik136"),
    )
