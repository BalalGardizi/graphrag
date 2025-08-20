import json
from datetime import datetime, timezone
from pathlib import Path
from graphiti_core.nodes import EpisodeType
from graphiti_core.utils.bulk_utils import RawEpisode

# ---- Base Class ----
class BaseDataIngestor:
    def ingest(self, source):
        raise NotImplementedError
    def to_json(self):
        raise NotImplementedError
    def to_episodes(self):
        raise NotImplementedError

# ---- Factory ----
class DataFactory:
    registry = {}

    @classmethod
    def register(cls, asset_type):
        def inner_wrapper(wrapped_class):
            cls.registry[asset_type] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def create(cls, asset_type, *args, **kwargs):
        if asset_type not in cls.registry:
            raise ValueError(f"Unknown asset type: {asset_type}")
        return cls.registry[asset_type](*args, **kwargs)

# ---- Ingesters ----
@DataFactory.register("contract")
class ContractIngestor(BaseDataIngestor):
    def __init__(self):
        self.contracts = []
    def ingest(self, source):
        self.contracts = json.loads(Path(source).read_text())
    def to_json(self):
        return self.contracts
    def to_episodes(self):
        return [
            RawEpisode(
                name=f"Contract-{c['customer_id']}",
                content=json.dumps(c),
                source_description="Energy contract data",
                source=EpisodeType.json,
                reference_time=datetime.now(timezone.utc)
            )
            for c in self.contracts
        ]
@DataFactory.register("price")
class PriceIngestor(BaseDataIngestor):
    def __init__(self):
        self.prices = []

    def ingest(self, source):
        self.prices = json.loads(Path(source).read_text())

    def to_json(self):
        return self.prices

    def to_episodes(self):
        episodes = []
        for p in self.prices:
            episodes.append(
                RawEpisode(
                    name=f"EnergyPrice-{p['date']}",
                    content=json.dumps(p),
                    source_description="Energy price per kWh for given date",
                    source=EpisodeType.json,
                    reference_time=datetime.fromisoformat(f"{p['date']}T00:00:00+00:00"),
                    # Include IDs/group_id that match the entity node(s) this price should connect to
                    group_id=f"Price_{p.get('location_id','default')}"
                )
            )
        return episodes

@DataFactory.register("conversation")
class ConversationIngestor(BaseDataIngestor):
    def __init__(self):
        self.history = []

    def ingest(self, source):
        self.history = json.loads(Path(source).read_text())

    def to_json(self):
        return self.history

    def to_episodes(self):
        # Group messages by thread_id
        threads = {}
        for msg in self.history:
            threads.setdefault(msg["thread_id"], []).append(msg)

        episodes = []
        for thread_id, messages in threads.items():
            # Sort by timestamp so the conversation flow is preserved
            messages.sort(key=lambda m: m["timestamp"])

            episodes.append(
                RawEpisode(
                    name=f"ChatbotConversation-{thread_id}",
                    content=json.dumps(messages),
                    source_description="Full customer-bot conversation history",
                    source=EpisodeType.json,
                    # reference_time could be first or last message — here I use the last
                    reference_time=datetime.fromisoformat(
                        messages[-1]["timestamp"].replace("Z", "+00:00")
                    ),
                    group_id=thread_id  # helps link related content later
                )
            )

        return episodes
