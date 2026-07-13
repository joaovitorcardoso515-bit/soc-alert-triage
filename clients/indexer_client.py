from opensearchpy import OpenSearch
from config import (
    INDEXER_HOST,
    INDEXER_USER,
    INDEXER_PASSWORD
)


class IndexerClient:

    def __init__(self):

        self.client = OpenSearch(
            hosts=[INDEXER_HOST],
            http_auth=(INDEXER_USER, INDEXER_PASSWORD),
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )

    def health(self):
        return self.client.cluster.health()