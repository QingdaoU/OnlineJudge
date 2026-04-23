# submission/tasks.py
import dramatiq
import logging
from utils.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

@dramatiq.actor(max_retries=3)
def sync_submission_to_neo4j(submission_id):
    from submission.models import Submission
    from problem.models import Problem

    try:
        sub = Submission.objects.select_related('problem').get(id=submission_id)
    except Submission.DoesNotExist:
        logger.error(f"Submission {submission_id} not found")
        return

    client = neo4j_client
    user_id = sub.user_id
    username = sub.username
    problem_id = sub.problem.id
    problem__id = sub.problem._id
    problem_title = sub.problem.title
    problem_difficulty = sub.problem.difficulty
    result = str(sub.result)
    language = sub.language
    create_time = sub.create_time.isoformat()

    # 获取题目标签列表
    tags = [tag.name for tag in sub.problem.tags.all()]

    params = {
        'user_id': user_id,
        'username': username,
        'problem_id': problem_id,
        '_id': problem__id,
        'title': problem_title,
        'difficulty': problem_difficulty,
        'sub_id': sub.id,
        'result': result,
        'language': language,
        'create_time': create_time,
        'tags': tags,
    }

    queries = [
        # 用户节点
        "MERGE (u:User {user_id: $user_id}) SET u.username = $username",
        # 题目节点
        "MERGE (p:Problem {problem_id: $problem_id}) SET p._id = $_id, p.title = $title, p.difficulty = $difficulty",
        # 提交节点
        "MERGE (s:Submission {submission_id: $sub_id}) SET s.result = $result, s.language = $language, s.create_time = datetime($create_time)",
        # 用户 - 提交关系
        "MATCH (u:User {user_id: $user_id}) MATCH (s:Submission {submission_id: $sub_id}) MERGE (u)-[:SUBMITTED]->(s)",
        # 提交 - 题目关系
        "MATCH (s:Submission {submission_id: $sub_id}) MATCH (p:Problem {problem_id: $problem_id}) MERGE (s)-[:FOR]->(p)",
    ]

    # 知识点关系（如果存在标签）
    if tags:
        queries.append(
            """
            MATCH (p:Problem {problem_id: $problem_id})
            MATCH (t:Topic) WHERE t.name IN $tags
            MERGE (p)-[:BELONGS_TO]->(t)
            """
        )

    try:
        with client._driver.session() as session:
            for query in queries:
                session.run(query, params)
        logger.info(f"Synced submission {submission_id} to Neo4j")
    except Exception as e:
        logger.exception(f"Failed to sync submission {submission_id}: {e}")
        raise