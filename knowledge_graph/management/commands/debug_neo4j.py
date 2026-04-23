from django.core.management.base import BaseCommand
from utils.neo4j_client import neo4j_client


class Command(BaseCommand):
    help = '调试 Neo4j 知识图谱：检查节点、关系和路径'

    def add_arguments(self, parser):
        parser.add_argument('--start', type=str, help='起始知识点')
        parser.add_argument('--end', type=str, help='目标知识点')
        parser.add_argument('--check-all', action='store_true', help='检查所有知识点和关系')

    def handle(self, *args, **options):
        if options['check_all']:
            self.check_all()

        if options['start'] and options['end']:
            self.test_path(options['start'], options['end'])

        if not options['check_all'] and not (options['start'] and options['end']):
            self.check_all()

    def check_all(self):
        """检查所有知识点和关系"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('检查所有 Topic 节点')
        self.stdout.write('=' * 60)

        result = neo4j_client.run_query("""
            MATCH (t:Topic)
            RETURN t.name AS name
            ORDER BY t.name
        """)

        self.stdout.write(f'共找到 {len(result)} 个知识点：')
        topics = []
        for i, r in enumerate(result, 1):
            self.stdout.write(f'  {i}. {r["name"]}')
            topics.append(r['name'])
        self.stdout.write('')

        self.stdout.write('=' * 60)
        self.stdout.write('检查 PREREQUISITE_OF 关系')
        self.stdout.write('=' * 60)

        result = neo4j_client.run_query("""
            MATCH (t1:Topic)-[:PREREQUISITE_OF]->(t2:Topic)
            RETURN t1.name AS source, t2.name AS target
            ORDER BY t1.name, t2.name
        """)

        self.stdout.write(f'共找到 {len(result)} 条关系：')
        for i, r in enumerate(result, 1):
            self.stdout.write(f'  {i}. {r["source"]} -> {r["target"]}')
        self.stdout.write('')

        return topics

    def test_path(self, start, end):
        """测试两个知识点之间的路径"""
        self.stdout.write('=' * 60)
        self.stdout.write(f'测试路径: {start} -> {end}')
        self.stdout.write('=' * 60)

        # 检查知识点是否存在
        start_exists = neo4j_client.run_query(
            'MATCH (t:Topic {name: $name}) RETURN t.name AS name',
            {'name': start}
        )
        end_exists = neo4j_client.run_query(
            'MATCH (t:Topic {name: $name}) RETURN t.name AS name',
            {'name': end}
        )

        if start_exists:
            self.stdout.write(f'✓ 知识点 "{start}" 存在')
        else:
            self.stdout.write(f'✗ 知识点 "{start}" 不存在')

        if end_exists:
            self.stdout.write(f'✓ 知识点 "{end}" 存在')
        else:
            self.stdout.write(f'✗ 知识点 "{end}" 不存在')

        self.stdout.write('')

        if not start_exists or not end_exists:
            self.stdout.write('知识点不存在，无法查询路径')
            return

        # 有向查询
        query1 = """
        MATCH (start:Topic {name: $start}), (end:Topic {name: $end})
        MATCH path = shortestPath((start)-[:PREREQUISITE_OF*..10]->(end))
        RETURN nodes(path) AS nodes
        """
        result1 = neo4j_client.run_query(query1, {'start': start, 'end': end})

        if result1:
            nodes = [n['name'] for n in result1[0]['nodes']]
            self.stdout.write(f'✓ 有向查询成功: {" -> ".join(nodes)}')
        else:
            self.stdout.write('✗ 有向查询失败')

        # 无向查询
        query2 = """
        MATCH (start:Topic {name: $start}), (end:Topic {name: $end})
        MATCH path = shortestPath((start)-[:PREREQUISITE_OF*..10]-(end))
        RETURN nodes(path) AS nodes
        """
        result2 = neo4j_client.run_query(query2, {'start': start, 'end': end})

        if result2:
            nodes = [n['name'] for n in result2[0]['nodes']]
            self.stdout.write(f'✓ 无向查询成功: {" -> ".join(nodes)}')
        else:
            self.stdout.write('✗ 无向查询失败')

        self.stdout.write('')
