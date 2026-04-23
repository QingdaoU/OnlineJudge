# utils/neo4j_client.py
import os
from neo4j import GraphDatabase

class Neo4jClient:
    def __init__(self):
        uri = os.environ.get('NEO4J_URL', 'bolt://oj-neo4j:7687')
        user = os.environ.get('NEO4J_USER', 'neo4j')
        password = os.environ.get('NEO4J_PASSWORD', 'pzq4869')
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def run_query(self, query, parameters=None):
        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

# 全局单例
neo4j_client = Neo4jClient()