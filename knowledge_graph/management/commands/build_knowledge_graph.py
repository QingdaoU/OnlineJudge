from django.core.management.base import BaseCommand
from utils.neo4j_client import neo4j_client
from problem.models import Problem, ProblemTag
from account.models import User
from submission.models import Submission

class Command(BaseCommand):
    help = '从 PostgreSQL 同步数据到 Neo4j 知识图谱'

    def handle(self, *args, **options):
        client = neo4j_client

        # 1. 清空图数据库
        self.stdout.write('清空 Neo4j 数据库...')
        client.run_query("MATCH (n) DETACH DELETE n")

        # 2. 导入知识点 (ProblemTag)
        self.stdout.write('导入知识点...')
        tags = ProblemTag.objects.all()
        tag_count = 0
        for tag in tags:
            client.run_query(
                "MERGE (:Topic {name: $name})",
                {'name': tag.name}
            )
            tag_count += 1
        self.stdout.write(f'  已导入 {tag_count} 个知识点')

        # 3. 导入题目
        self.stdout.write('导入题目...')
        problems = Problem.objects.filter(visible=True)
        problem_count = 0
        for problem in problems:
            client.run_query(
                """
                MERGE (p:Problem {problem_id: $id})
                SET p._id = $_id,
                    p.title = $title,
                    p.difficulty = $difficulty,
                    p.source = $source,
                    p.time_limit = $time_limit,
                    p.memory_limit = $memory_limit
                """,
                {
                    'id': problem.id,
                    '_id': problem._id,
                    'title': problem.title,
                    'difficulty': problem.difficulty,
                    'source': problem.source or '',
                    'time_limit': problem.time_limit,
                    'memory_limit': problem.memory_limit
                }
            )
            # 关联知识点
            for tag in problem.tags.all():
                client.run_query(
                    """
                    MATCH (p:Problem {problem_id: $pid})
                    MATCH (t:Topic {name: $tname})
                    MERGE (p)-[:BELONGS_TO]->(t)
                    """,
                    {'pid': problem.id, 'tname': tag.name}
                )
            problem_count += 1
            if problem_count % 100 == 0:
                self.stdout.write(f'  已处理 {problem_count} 道题目...')
        self.stdout.write(f'  共导入 {problem_count} 道题目')

        # 4. 导入用户
        self.stdout.write('导入用户...')
        users = User.objects.all()
        user_count = 0
        for user in users:
            client.run_query(
                """
                MERGE (u:User {user_id: $id})
                SET u.username = $username,
                    u.email = $email,
                    u.admin_type = $admin_type
                """,
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email or '',
                    'admin_type': user.admin_type
                }
            )
            user_count += 1
        self.stdout.write(f'  已导入 {user_count} 个用户')

        # 5. 导入提交记录 (限制数量避免内存压力)
        self.stdout.write('导入提交记录 (最近50000条)...')
        submissions = Submission.objects.order_by('-create_time')[:50000]
        sub_count = 0
        for sub in submissions:
            client.run_query(
                """
                MERGE (s:Submission {submission_id: $id})
                SET s.result = $result,
                    s.language = $language,
                    s.create_time = datetime($time)
                WITH s
                MATCH (u:User {user_id: $uid})
                MATCH (p:Problem {problem_id: $pid})
                MERGE (u)-[:SUBMITTED]->(s)
                MERGE (s)-[:FOR]->(p)
                """,
                {
                    'id': sub.id,                     # 注意 sub.id 是字符串
                    'result': str(sub.result),
                    'language': sub.language,
                    'time': sub.create_time.isoformat(),
                    'uid': sub.user_id,
                    'pid': sub.problem_id
                }
            )
            sub_count += 1
            if sub_count % 1000 == 0:
                self.stdout.write(f'  已处理 {sub_count} 条提交...')
        self.stdout.write(f'  共导入 {sub_count} 条提交记录')

        self.stdout.write(self.style.SUCCESS('知识图谱构建完成！'))
