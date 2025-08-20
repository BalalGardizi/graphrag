#!/usr/bin/env python3
import argparse
import asyncio
import os
from dotenv import load_dotenv
from graphiti_core import Graphiti
from graphiti_core.utils.maintenance.graph_data_operations import clear_data
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

async def main():
    parser = argparse.ArgumentParser(description="Bootstrap Neo4j Graphiti schema and optionally clear data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear all existing graph data before creating indices/constraints."
    )
    args = parser.parse_args()

    load_dotenv()
    os.environ["OPENAI_API_KEY"] = "abc"  # remove if not needed for your LLM choice

    api_key = os.environ['GOOGLE_API_KEY']
    os.environ["SEMAPHORE_LIMIT"] = "1"

    # Init Graphiti with Gemini clients (same config you use elsewhere)
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

    # Optional destructive reset
    if args.reset:
        print("⚠ Clearing all existing graph data...")
        await clear_data(client.driver)

    # Always (re)build indices & constraints in bootstrap
    print("🔧 Building indices and constraints...")
    await client.build_indices_and_constraints()


if __name__ == "__main__":
    asyncio.run(main())
