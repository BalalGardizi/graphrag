import asyncio
from pathlib import Path
from factories import DataFactory
import os
import pprint
from dotenv import load_dotenv

from graphiti_core import Graphiti
from graphiti_core.edges import EntityEdge
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient


def print_facts(edges):
    print("\n".join([edge.fact for edge in edges]))


def pretty_print(entity: EntityEdge | list[EntityEdge]):
    if isinstance(entity, EntityEdge):
        data = {k: v for k, v in entity.model_dump().items() if k != 'fact_embedding'}
    elif isinstance(entity, list):
        data = [{k: v for k, v in e.model_dump().items() if k != 'fact_embedding'} for e in entity]
    else:
        pprint.pprint(entity)
        return
    pprint.pprint(data)


def edges_to_facts_string(entities: list[EntityEdge]):
    return '-' + '\n- '.join([edge.fact for edge in entities])


async def main():
    load_dotenv()

    os.environ["OPENAI_API_KEY"] = "abc"
    api_key = os.environ['GOOGLE_API_KEY']
    os.environ["SEMAPHORE_LIMIT"] = "1"

    # Connect to existing DB with schema already set up by db_bootstrap.py
    client = Graphiti(
        "bolt://localhost:7687",
        "neo4j",
        "Password123",
        llm_client=GeminiClient(
            config=LLMConfig(
                api_key=api_key,
                model="gemini-2.0-flash-lite"
            )
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=api_key,
                embedding_model="embedding-001"
            )
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(
                api_key=api_key,
                model="gemini-2.5-flash-lite-preview-06-17"
            )
        )
    )

    # Asset sources
    sources = {
#        "contract": "data/contracts_generated.json",
        "price": "data/prices.json",
        #"conversation": "data/conversations.json"
    }

    all_episodes = []
    for asset_type, path in sources.items():
        ingester = DataFactory.create(asset_type)
        ingester.ingest(path)
        all_episodes.extend(ingester.to_episodes())

    # Free tier API constraints
    CHUNK_SIZE = 1
    DELAY_SECONDS = 20

    for i in range(0, len(all_episodes), CHUNK_SIZE):
        chunk = all_episodes[i:i + CHUNK_SIZE]
        await client.add_episode_bulk(chunk)
        await asyncio.sleep(DELAY_SECONDS)

    # Example search
    results = await client.search('What was the customer_id')

    print('\nSearch Results:')
    for result in results:
        print(f'UUID: {result.uuid}')
        print(f'Fact: {result.fact}')
        if getattr(result, 'valid_at', None):
            print(f'Valid from: {result.valid_at}')
        if getattr(result, 'invalid_at', None):
            print(f'Valid until: {result.invalid_at}')
        print('---')

    # Optional rerank example
    if results:
        center_node_uuid = results[0].source_node_uuid
        print('\nReranking search results based on graph distance:')
        print(f'Using center node UUID: {center_node_uuid}')

        reranked_results = await client.search(
            'show customers',
            center_node_uuid=center_node_uuid
        )

        print('\nReranked Search Results:')
        for result in reranked_results:
            print(f'UUID: {result.uuid}')
            print(f'Fact: {result.fact}')
            if getattr(result, 'valid_at', None):
                print(f'Valid from: {result.valid_at}')
            if getattr(result, 'invalid_at', None):
                print(f'Valid until: {result.invalid_at}')
            print('---')


if __name__ == "__main__":
    asyncio.run(main())
