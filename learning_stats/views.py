from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, FloatField, F
from django.db.models.functions import Cast
from problem.models import Problem, ProblemTag
from submission.models import Submission, JudgeStatus
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from utils.neo4j_client import neo4j_client
import logging

logger = logging.getLogger(__name__)

@login_required
def learning_stats(request):
    user = request.user
    total_submissions = Submission.objects.filter(user_id=user.id).count()
    total_ac = Submission.objects.filter(user_id=user.id, result=JudgeStatus.ACCEPTED).count()
    accuracy = round(total_ac / total_submissions * 100, 1) if total_submissions else 0

    # ---------- 知识点统计优化 ----------
    # 只统计用户实际提交过的知识点，并按提交总数降序排列，取前8个用于雷达图
    tag_stats = []
    # 先获取用户提交过的所有题目ID
    user_problem_ids = Submission.objects.filter(user_id=user.id).values_list('problem_id', flat=True).distinct()
    # 获取这些题目关联的知识点及其提交统计
    tags_with_data = ProblemTag.objects.filter(problem__id__in=user_problem_ids).annotate(
        total=Count('problem__submission', filter=Q(problem__submission__user_id=user.id)),
        ac=Count('problem__submission', filter=Q(problem__submission__user_id=user.id) & Q(problem__submission__result=JudgeStatus.ACCEPTED))
    ).filter(total__gt=0).order_by('-total')[:8]  # 只取提交数最多的前8个知识点

    for tag in tags_with_data:
        acc_rate = round(tag.ac / tag.total * 100, 1) if tag.total else 0
        tag_stats.append({
            'tag_name': tag.name,
            'total': tag.total,
            'ac': tag.ac,
            'accuracy': acc_rate,
        })
    # 按正确率升序排序（便于前端展示薄弱项）
    tag_stats.sort(key=lambda x: x['accuracy'])

    # ---------- 击败百分比 ----------
    beat_percent = get_beat_percent(user)

    # ---------- 语言统计优化 ----------
    # 对语言名称进行规范化处理：统一小写，去除常见版本后缀
    from django.db.models.functions import Lower
    lang_stats = []
    # 先获取原始语言分组
    raw_lang_groups = Submission.objects.filter(user_id=user.id).values('language').annotate(
        total=Count('id'),
        ac=Count('id', filter=Q(result=JudgeStatus.ACCEPTED))
    )
    # 使用字典合并相同语言（忽略大小写和版本差异）
    merged_langs = {}
    for group in raw_lang_groups:
        raw_lang = group['language']
        # 规范化语言名称：只保留字母数字，统一小写，去除常见版本号
        import re
        normalized = re.sub(r'[^a-zA-Z]', '', raw_lang).lower()
        # 常见语言别名映射（可根据实际情况扩展）
        alias_map = {
            'cpp': 'c++',
            'cplusplus': 'c++',
            'py': 'python',
            'python3': 'python',
            'js': 'javascript',
            'node': 'javascript',
            'golang': 'go',
        }
        display_lang = alias_map.get(normalized, raw_lang)  # 显示名可使用原始名或映射名
        key = display_lang.lower()
        if key not in merged_langs:
            merged_langs[key] = {
                'lang_name': display_lang,
                'total': 0,
                'ac': 0,
            }
        merged_langs[key]['total'] += group['total']
        merged_langs[key]['ac'] += group['ac']

    for key, data in merged_langs.items():
        total = data['total']
        ac = data['ac']
        acc_rate = round(ac / total * 100, 1) if total else 0
        lang_stats.append({
            'lang_name': data['lang_name'],
            'total': total,
            'ac': ac,
            'accuracy': acc_rate,
        })
    lang_stats.sort(key=lambda x: x['accuracy'])

    data = {
        'total_submissions': total_submissions,
        'total_ac': total_ac,
        'accuracy': accuracy,
        'beat_percent': beat_percent,
        'tags': tag_stats,
        'lang_stats': lang_stats,
    }
    return JsonResponse(data)

def get_beat_percent(user):
    user_stats = Submission.objects.filter(user_id=user.id).aggregate(
        total_sub=Count('id'),
        total_ac=Count('id', filter=Q(result=JudgeStatus.ACCEPTED))
    )
    if user_stats['total_sub'] == 0:
        return 0.0
    user_accuracy = user_stats['total_ac'] / user_stats['total_sub'] * 100
    all_users_stats = Submission.objects.values('user_id').annotate(
        total_sub=Count('id'),
        total_ac=Count('id', filter=Q(result=JudgeStatus.ACCEPTED))
    ).filter(total_sub__gt=0).annotate(
        accuracy=Cast(F('total_ac'), FloatField()) / Cast(F('total_sub'), FloatField()) * 100
    ).order_by('-accuracy')
    higher_count = all_users_stats.filter(accuracy__gt=user_accuracy).count()
    total_users = all_users_stats.count()
    if total_users == 0:
        return 0.0
    beat = (total_users - higher_count) / total_users * 100
    return round(beat, 1)

@login_required
def learning_trend(request):
    days = int(request.GET.get('days', 7))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    submissions = Submission.objects.filter(
        user_id=request.user.id,
        create_time__date__gte=start_date,
        create_time__date__lte=end_date
    ).annotate(date=TruncDate('create_time')).values('date').annotate(
        total=Count('id'),
        ac=Count('id', filter=Q(result=JudgeStatus.ACCEPTED))
    ).order_by('date')
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    result = []
    for d in date_range:
        item = next((s for s in submissions if s['date'] == d), None)
        if item and item['total'] > 0:
            rate = round(item['ac'] / item['total'] * 100, 1)
        else:
            rate = 0
        result.append({
            'date': d.strftime('%m/%d'),
            'accuracy': rate
        })
    return JsonResponse({'trend': result})

@login_required
def recommend(request):
    user = request.user
    username = user.username
    limit = int(request.GET.get('limit', 5))
    offset = int(request.GET.get('offset', 0))

    logger.warning(f"=== 推荐请求：用户 {username}, limit={limit}, offset={offset} ===")

    graph_recs = get_graph_recommendations(username, limit=50)
    logger.warning(f"图谱召回结果数量: {len(graph_recs)}")

    if len(graph_recs) < limit + offset:
        logger.warning("图谱召回不足，使用热度兜底")
        hot_recs = get_hot_recommendations(user, limit=50)
        logger.warning(f"热度兜底结果数量: {len(hot_recs)}")
        graph_recs.extend(hot_recs)
    else:
        logger.warning("图谱召回充足，不使用热度兜底")

    seen_ids = set()
    unique_recs = []
    for rec in graph_recs:
        pid = rec['id']
        if pid not in seen_ids:
            seen_ids.add(pid)
            unique_recs.append(rec)

    paged_recs = unique_recs[offset:offset+limit]
    total = len(unique_recs)

    problem_ids = [rec['id'] for rec in paged_recs]
    problems_map = {
        p.id: p for p in Problem.objects.filter(id__in=problem_ids).prefetch_related('tags')
    }

    data = []
    for rec in paged_recs:
        problem = problems_map.get(rec['id'])
        if not problem:
            continue
        data.append({
            '_id': problem._id,
            'title': problem.title,
            'difficulty': problem.difficulty,
            'tags': [tag.name for tag in problem.tags.all()],
            'reason': rec['reason'],
        })

    logger.warning(f"最终返回推荐数量: {len(data)}")
    return JsonResponse({'recommendations': data, 'total': total})

def get_graph_recommendations(username, limit=20):
    client = neo4j_client
    recs = []
    seen_ids = set()

    def add_rec(problem_id, reason, score):
        if problem_id not in seen_ids:
            seen_ids.add(problem_id)
            recs.append({'id': problem_id, 'reason': reason, 'score': score})

    # 1. 前置知识点推荐（学完前置知识点后推荐当前知识点）
    prereq_query = """
    MATCH (u:User {username: $username})-[:SUBMITTED]->(s:Submission)-[:FOR]->(p:Problem)-[:BELONGS_TO]->(t:Topic)
    WHERE s.result = '0'
    WITH u, t, count(DISTINCT s) AS ac_count
    WHERE ac_count >= 2
    MATCH (t)-[:PREREQUISITE_OF]->(next_topic:Topic)
    MATCH (next_topic)<-[:BELONGS_TO]-(rec:Problem)
    WHERE NOT EXISTS { MATCH (u)-[:SUBMITTED]->(:Submission)-[:FOR]->(rec) }
    RETURN DISTINCT rec.problem_id AS id, rec._id AS display_id, rec.title AS title,
           t.name AS mastered_topic, next_topic.name AS next_topic,
           rec.accepted_number AS ac_num
    ORDER BY rec.accepted_number DESC
    LIMIT 10
    """
    try:
        result = client.run_query(prereq_query, {'username': username})
        for r in result:
            add_rec(r['id'], f"您已掌握「{r['mastered_topic']}」，推荐学习「{r['next_topic']}」", score=90)
    except Exception as e:
        logger.error(f"前置知识点推荐查询失败: {e}")

    # 2. 薄弱知识点巩固（错误率高且提交数足够的知识点）
    weak_query = """
    MATCH (u:User {username: $username})-[:SUBMITTED]->(s:Submission)-[:FOR]->(p:Problem)-[:BELONGS_TO]->(t:Topic)
    WITH u, t, count(s) AS total,
         sum(CASE WHEN s.result = '0' THEN 1 ELSE 0 END) AS ac_count
    WHERE total >= 3
    WITH t, total, ac_count, (total - ac_count) * 1.0 / total AS error_rate
    WHERE error_rate > 0.3
    ORDER BY error_rate DESC, total DESC
    LIMIT 3
    MATCH (t)<-[:BELONGS_TO]-(rec:Problem)
    WHERE NOT EXISTS {
        MATCH (u)-[:SUBMITTED]->(sub:Submission)-[:FOR]->(rec)
        WHERE sub.result = '0'
    }
    RETURN DISTINCT rec.problem_id AS id, rec._id AS display_id, rec.title AS title,
           t.name AS weak_topic, rec.difficulty AS difficulty,
           rec.accepted_number AS ac_num
    ORDER BY rec.accepted_number DESC
    LIMIT 10
    """
    try:
        result = client.run_query(weak_query, {'username': username})
        for r in result:
            add_rec(r['id'], f"巩固薄弱知识点「{r['weak_topic']}」", score=85)
    except Exception as e:
        logger.error(f"薄弱知识点巩固查询失败: {e}")

    # 3. 擅长知识点拓展（基于用户AC最多的知识点推荐同难度新题）
    strength_query = """
    MATCH (u:User {username: $username})-[:SUBMITTED]->(s:Submission)-[:FOR]->(p:Problem)-[:BELONGS_TO]->(t:Topic)
    WHERE s.result = '0'
    WITH u, t, p, count(s) AS ac_count
    WHERE ac_count >= 1
    WITH u, t, collect(DISTINCT p.difficulty) AS difficulties, ac_count
    ORDER BY ac_count DESC
    LIMIT 3
    UNWIND difficulties AS diff
    MATCH (t)<-[:BELONGS_TO]-(rec:Problem)
    WHERE rec.difficulty IN difficulties
    AND NOT EXISTS { MATCH (u)-[:SUBMITTED]->(:Submission)-[:FOR]->(rec) }
    RETURN DISTINCT rec.problem_id AS id, rec._id AS display_id, rec.title AS title,
           t.name AS strength_topic, rec.difficulty AS difficulty
    ORDER BY rec.accepted_number DESC
    LIMIT 10
    """
    try:
        result = client.run_query(strength_query, {'username': username})
        for r in result:
            add_rec(r['id'], f"拓展擅长知识点「{r['strength_topic']}」的同难度题目", score=75)
    except Exception as e:
        logger.error(f"擅长知识点拓展查询失败: {e}")

    # 4. 协同过滤召回（相似用户推荐）
    cf_query = """
    MATCH (u:User {username: $username})-[:SUBMITTED]->(s1:Submission)-[:FOR]->(p:Problem)
    WHERE s1.result = '0'
    WITH u, collect(DISTINCT p) AS u_ac
    MATCH (other:User)-[:SUBMITTED]->(s2:Submission)-[:FOR]->(p)
    WHERE s2.result = '0' AND other <> u AND p IN u_ac
    WITH u, u_ac, other, count(DISTINCT p) AS common
    WHERE common >= 2
    ORDER BY common DESC
    LIMIT 5
    MATCH (other)-[:SUBMITTED]->(s3:Submission)-[:FOR]->(rec:Problem)
    WHERE s3.result = '0' AND NOT rec IN u_ac
    RETURN DISTINCT rec.problem_id AS id, rec._id AS display_id, rec.title AS title
    ORDER BY rec.accepted_number DESC
    LIMIT 10
    """
    try:
        result = client.run_query(cf_query, {'username': username})
        for r in result:
            add_rec(r['id'], "与您学习路径相似的用户也做了此题", score=65)
    except Exception as e:
        logger.error(f"协同过滤查询失败: {e}")

    # 5. 难度递进推荐（从用户已AC的题目难度出发推荐更高难度）
    progression_query = """
    MATCH (u:User {username: $username})-[:SUBMITTED]->(s:Submission)-[:FOR]->(p:Problem)
    WHERE s.result = '0'
    WITH u, collect(DISTINCT p.difficulty) AS user_difficulties
    UNWIND user_difficulties AS diff
    WITH u, diff
    ORDER BY diff
    WITH u, collect(diff)[-1] AS max_diff
    MATCH (rec:Problem)
    WHERE NOT EXISTS { MATCH (u)-[:SUBMITTED]->(:Submission)-[:FOR]->(rec) }
    AND (
        (max_diff = 'Low' AND rec.difficulty IN ['Low', 'Mid']) OR
        (max_diff = 'Mid' AND rec.difficulty IN ['Mid', 'High'])
    )
    RETURN rec.problem_id AS id, rec._id AS display_id, rec.title AS title,
           rec.difficulty AS difficulty
    ORDER BY rec.accepted_number DESC
    LIMIT 10
    """
    try:
        result = client.run_query(progression_query, {'username': username})
        for r in result:
            add_rec(r['id'], f"挑战更高难度「{r['difficulty']}」的题目", score=60)
    except Exception as e:
        logger.error(f"难度递进推荐查询失败: {e}")

    # 按分数降序排序后返回
    recs.sort(key=lambda x: x['score'], reverse=True)
    return recs[:limit]

def get_hot_recommendations(user, limit=20):
    done_ids = Submission.objects.filter(user_id=user.id).values_list('problem_id', flat=True).distinct()
    problems = Problem.objects.exclude(id__in=done_ids).order_by('-accepted_number')[:limit]
    recs = []
    for p in problems:
        user_tags = ProblemTag.objects.filter(
            problem__submission__user_id=user.id,
            problem__submission__result=JudgeStatus.ACCEPTED
        ).distinct()
        common_tags = list(p.tags.filter(id__in=user_tags).values_list('name', flat=True))
        if common_tags:
            # 使用第一个共同标签作为理由，风格与内容召回一致
            reason = f"基于您常做的「{common_tags[0]}」题目推荐"
        else:
            # 若无共同标签，则根据题目自身标签推荐
            first_tag = p.tags.first()
            if first_tag:
                reason = f"热门「{first_tag.name}」题目推荐"
            else:
                reason = "热门题目推荐"
        recs.append({
            'id': p.id,
            'reason': reason
        })
    return recs

@login_required
def learning_path(request):
    user = request.user
    username = user.username
    target_topic = request.GET.get('target_topic')
    start_topic = request.GET.get('start_topic')  # 新增可选参数

    if not target_topic:
        return JsonResponse({'error': 'target_topic 参数缺失'}, status=400)

    # 如果前端没有传起始知识点，则自动使用用户最薄弱的
    if not start_topic:
        start_topic = get_user_weakest_topic(username)
        if not start_topic:
            return JsonResponse({'error': '无足够数据判断薄弱知识点'}, status=404)

    path_topics = get_shortest_path(start_topic, target_topic)
    if not path_topics:
        return JsonResponse({'error': f'未找到从「{start_topic}」到「{target_topic}」的学习路径'}, status=404)

    enriched_path = enrich_path_with_problems(path_topics, username)

    return JsonResponse({
        'start_topic': start_topic,  # 返回实际使用的起点
        'target_topic': target_topic,
        'path': enriched_path
    })

def get_user_weakest_topic(username):
    """返回用户错误率最高的知识点名称"""
    query = """
    MATCH (u:User {username: $username})-[:SUBMITTED]->(s:Submission)-[:FOR]->(p:Problem)-[:BELONGS_TO]->(t:Topic)
    WITH t, count(s) AS total, sum(CASE WHEN s.result <> '0' THEN 1 ELSE 0 END) AS wrong
    WHERE total >= 3
    RETURN t.name AS topic, wrong * 1.0 / total AS error_rate
    ORDER BY error_rate DESC
    LIMIT 1
    """
    result = neo4j_client.run_query(query, {'username': username})
    return result[0]['topic'] if result else None

def get_shortest_path(start_topic, end_topic):
    """查询两个知识点之间的最短路径（使用无向查询）"""
    query = """
    MATCH (start:Topic {name: $start}), (end:Topic {name: $end})
    MATCH path = shortestPath((start)-[:PREREQUISITE_OF*..10]-(end))
    RETURN nodes(path) AS nodes
    """
    result = neo4j_client.run_query(query, {'start': start_topic, 'end': end_topic})
    if not result:
        return None
    nodes = result[0]['nodes']
    return [node['name'] for node in nodes]

def enrich_path_with_problems(path_topics, username):
    """为路径上每个知识点推荐一道用户未做过的代表性题目（按AC数排序）"""
    enriched = []
    for topic in path_topics:
        query = """
        MATCH (t:Topic {name: $topic})<-[:BELONGS_TO]-(p:Problem)
        WHERE NOT EXISTS {
            MATCH (u:User {username: $username})-[:SUBMITTED]->(:Submission)-[:FOR]->(p)
        }
        RETURN p.problem_id AS id, p._id AS display_id, p.title AS title, p.difficulty AS difficulty
        ORDER BY p.accepted_number DESC
        LIMIT 1
        """
        result = neo4j_client.run_query(query, {'topic': topic, 'username': username})
        if result:
            enriched.append({
                'topic': topic,
                'problem': result[0]
            })
        else:
            enriched.append({'topic': topic, 'problem': None})
    return enriched

from django.http import JsonResponse
from utils.neo4j_client import neo4j_client

def knowledge_graph_overview(request):
    """
    返回知识图谱概览数据，用于首页可视化
    优化版：直接返回所有节点和边，避免复杂循环
    """
    # 查询所有节点（限制最多返回200个节点，防止前端渲染卡顿）
    nodes_query = """
    MATCH (t:Topic)
    RETURN DISTINCT t.name AS name
    LIMIT 200
    """
    nodes_result = neo4j_client.run_query(nodes_query)
    nodes = [{'name': record['name']} for record in nodes_result]

    # 查询所有边（只保留两端节点都存在的边）
    edges_query = """
    MATCH (t1:Topic)-[:PREREQUISITE_OF]->(t2:Topic)
    RETURN DISTINCT t1.name AS source, t2.name AS target
    LIMIT 500
    """
    edges_result = neo4j_client.run_query(edges_query)
    edges = [{'source': record['source'], 'target': record['target']} for record in edges_result]

    return JsonResponse({'nodes': nodes, 'edges': edges})