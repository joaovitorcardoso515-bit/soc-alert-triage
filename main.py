from clients.indexer_client import IndexerClient

client = IndexerClient()

health = client.health()

print(health)