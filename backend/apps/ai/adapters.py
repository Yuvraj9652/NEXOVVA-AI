from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class InboundMessage:
    sender_identity: str  # Email address or Phone number
    content: str
    channel_type: str  # EMAIL, WHATSAPP, WEB
    metadata: dict = None


class InboundChannelAdapter(ABC):
    @abstractmethod
    def parse_request(self, request_data: dict) -> InboundMessage:
        """Parses raw webhook payloads into a unified InboundMessage structure."""
        pass
