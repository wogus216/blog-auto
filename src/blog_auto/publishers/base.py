from __future__ import annotations

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from blog_auto import config


@dataclass
class PublishRequest:
    title: str
    body_md: str
    tags: list[str]
    category: str
    mode: Literal["draft", "publish", "semi", "schedule"] = "draft"
    schedule_at: str | None = None
    cta_url: str | None = None
    cta_text: str | None = None


@dataclass
class PublishResult:
    url: str | None
    ok: bool
    note: str = ""


class BasePublisher(ABC):
    platform: str

    @abstractmethod
    def publish(self, req: PublishRequest) -> PublishResult: ...

    @staticmethod
    def human_pause() -> None:
        time.sleep(random.uniform(config.MIN_DELAY / 60, config.MAX_DELAY / 60))

    @staticmethod
    def tiny_pause() -> None:
        time.sleep(random.uniform(0.3, 1.2))
