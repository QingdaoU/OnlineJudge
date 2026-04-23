from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from account.decorators import admin_role_required
from account.models import User, UserProfile
from problem.models import Problem
from submission.models import Submission, JudgeStatus
from contest.models import Contest
from utils.api import APIView


class DashboardAdminAPI(APIView):
    @admin_role_required
    def get(self, request):
        return self.success({
            "overview": self._get_overview(),
            "problem_stats": self._get_problem_stats(),
            "difficulty_distribution": self._get_difficulty_distribution(),
            "problem_completion": self._get_problem_completion(),
            "top_submitters": self._get_top_submitters(),
            "user_ranking": self._get_user_ranking(),
            "submission_stats": self._get_submission_stats(),
            "recent_activity": self._get_recent_activity(),
        })

    def _get_overview(self):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        now = timezone.now()

        total_users = User.objects.count()
        total_problems = Problem.objects.filter(contest__isnull=True).count()
        total_submissions = Submission.objects.count()
        total_contests = Contest.objects.count()

        today_submissions = Submission.objects.filter(create_time__gte=today).count()
        week_submissions = Submission.objects.filter(create_time__gte=week_ago).count()
        month_submissions = Submission.objects.filter(create_time__gte=month_ago).count()

        today_users = Submission.objects.filter(create_time__gte=today).values("user_id").distinct().count()
        week_users = Submission.objects.filter(create_time__gte=week_ago).values("user_id").distinct().count()

        # 基于时间计算进行中/即将开始的比赛
        active_contests = Contest.objects.filter(start_time__lte=now, end_time__gte=now).count()
        upcoming_contests = Contest.objects.filter(start_time__gt=now).count()

        return {
            "total_users": total_users,
            "total_problems": total_problems,
            "total_submissions": total_submissions,
            "total_contests": total_contests,
            "today_submissions": today_submissions,
            "week_submissions": week_submissions,
            "month_submissions": month_submissions,
            "today_active_users": today_users,
            "week_active_users": week_users,
            "active_contests": active_contests,
            "upcoming_contests": upcoming_contests,
        }

    def _get_problem_stats(self):
        problems = Problem.objects.filter(contest__isnull=True)
        total = problems.count()
        visible = problems.filter(visible=True).count()
        hidden = problems.filter(visible=False).count()

        total_submission_count = problems.aggregate(Sum("submission_number"))["submission_number__sum"] or 0
        total_accepted_count = problems.aggregate(Sum("accepted_number"))["accepted_number__sum"] or 0

        overall_pass_rate = 0
        if total_submission_count > 0:
            overall_pass_rate = round(total_accepted_count / total_submission_count * 100, 2)

        tags_stats = []
        from problem.models import ProblemTag
        for tag in ProblemTag.objects.all():
            count = tag.problem_set.filter(contest__isnull=True).count()
            if count > 0:
                tags_stats.append({"name": tag.name, "count": count})
        tags_stats.sort(key=lambda x: x["count"], reverse=True)

        return {
            "total": total,
            "visible": visible,
            "hidden": hidden,
            "total_submissions": total_submission_count,
            "total_accepted": total_accepted_count,
            "overall_pass_rate": overall_pass_rate,
            "tags_distribution": tags_stats[:10],
        }

    def _get_difficulty_distribution(self):
        problems = Problem.objects.filter(contest__isnull=True)

        difficulties = [
            {"name": "Low", "label": "简单", "count": 0, "pass_rate": 0},
            {"name": "Mid", "label": "中等", "count": 0, "pass_rate": 0},
            {"name": "High", "label": "困难", "count": 0, "pass_rate": 0},
        ]

        for item in difficulties:
            qs = problems.filter(difficulty=item["name"])
            count = qs.count()
            item["count"] = count
            if count > 0:
                sub_count = qs.aggregate(Sum("submission_number"))["submission_number__sum"] or 0
                ac_count = qs.aggregate(Sum("accepted_number"))["accepted_number__sum"] or 0
                if sub_count > 0:
                    item["pass_rate"] = round(ac_count / sub_count * 100, 2)

        return difficulties

    def _get_problem_completion(self):
        problems = Problem.objects.filter(
            contest__isnull=True, visible=True
        ).order_by("-accepted_number")[:10]

        result = []
        for p in problems:
            pass_rate = 0
            if p.submission_number > 0:
                pass_rate = round(p.accepted_number / p.submission_number * 100, 2)
            result.append({
                "id": p.id,
                "_id": p._id,
                "title": p.title,
                "difficulty": p.difficulty,
                "submission_count": p.submission_number,
                "accepted_count": p.accepted_number,
                "pass_rate": pass_rate,
            })

        hardest_problems = Problem.objects.filter(
            contest__isnull=True, visible=True, submission_number__gt=0
        ).order_by("accepted_number", "-submission_number")[:10]

        hardest_result = []
        for p in hardest_problems:
            pass_rate = round(p.accepted_number / p.submission_number * 100, 2)
            hardest_result.append({
                "id": p.id,
                "_id": p._id,
                "title": p.title,
                "difficulty": p.difficulty,
                "submission_count": p.submission_number,
                "accepted_count": p.accepted_number,
                "pass_rate": pass_rate,
            })

        return {
            "most_completed": result,
            "least_completed": hardest_result,
        }

    def _get_top_submitters(self):
        week_ago = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)

        profiles = UserProfile.objects.select_related("user").order_by("-submission_number")[:10]
        all_time = []
        for p in profiles:
            all_time.append({
                "user_id": p.user.id,
                "username": p.user.username,
                "real_name": p.real_name,
                "submission_count": p.submission_number,
                "accepted_count": p.accepted_number,
                "total_score": p.total_score,
            })

        week_submissions = Submission.objects.filter(create_time__gte=week_ago).values("user_id").annotate(
            sub_count=Count("id"),
            ac_count=Count("id", filter=Q(result=JudgeStatus.ACCEPTED))
        ).order_by("-sub_count")[:10]

        week_data = []
        for item in week_submissions:
            user = User.objects.filter(id=item["user_id"]).first()
            if user:
                week_data.append({
                    "user_id": user.id,
                    "username": user.username,
                    "real_name": getattr(user.userprofile, "real_name", None),
                    "submission_count": item["sub_count"],
                    "accepted_count": item["ac_count"],
                })

        return {
            "all_time": all_time,
            "this_week": week_data,
        }

    def _get_user_ranking(self):
        profiles = UserProfile.objects.select_related("user").filter(
            accepted_number__gt=0
        ).order_by("-accepted_number", "submission_number")[:20]

        result = []
        for rank, p in enumerate(profiles, 1):
            ac_rate = 0
            if p.submission_number > 0:
                ac_rate = round(p.accepted_number / p.submission_number * 100, 2)
            result.append({
                "rank": rank,
                "user_id": p.user.id,
                "username": p.user.username,
                "real_name": p.real_name,
                "accepted_count": p.accepted_number,
                "submission_count": p.submission_number,
                "ac_rate": ac_rate,
                "total_score": p.total_score,
            })

        return result

    def _get_submission_stats(self):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        total = Submission.objects.count()
        ac_count = Submission.objects.filter(result=JudgeStatus.ACCEPTED).count()
        global_ac_rate = 0
        if total > 0:
            global_ac_rate = round(ac_count / total * 100, 2)

        result_distribution = []
        status_map = {
            JudgeStatus.PENDING: "Pending",
            JudgeStatus.JUDGING: "Judging",
            JudgeStatus.ACCEPTED: "Accepted",
            JudgeStatus.WRONG_ANSWER: "Wrong Answer",
            JudgeStatus.CPU_TIME_LIMIT_EXCEEDED: "CPU Time Limit Exceeded",
            JudgeStatus.REAL_TIME_LIMIT_EXCEEDED: "Real Time Limit Exceeded",
            JudgeStatus.MEMORY_LIMIT_EXCEEDED: "Memory Limit Exceeded",
            JudgeStatus.RUNTIME_ERROR: "Runtime Error",
            JudgeStatus.COMPILE_ERROR: "Compile Error",
            JudgeStatus.SYSTEM_ERROR: "System Error",
            JudgeStatus.PARTIALLY_ACCEPTED: "Partially Accepted",
        }
        for status_code, status_name in status_map.items():
            count = Submission.objects.filter(result=status_code).count()
            if count > 0:
                result_distribution.append({
                    "status": status_name,
                    "status_code": status_code,
                    "count": count,
                })
        result_distribution.sort(key=lambda x: x["count"], reverse=True)

        language_distribution = []
        submissions = Submission.objects.values("language").annotate(count=Count("id")).order_by("-count")
        for item in submissions:
            if item["count"] > 0:
                language_distribution.append({
                    "language": item["language"],
                    "count": item["count"],
                })

        daily_submissions = []
        for i in range(7):
            day = today - timedelta(days=6 - i)
            next_day = day + timedelta(days=1)
            count = Submission.objects.filter(
                create_time__gte=day, create_time__lt=next_day
            ).count()
            ac = Submission.objects.filter(
                create_time__gte=day, create_time__lt=next_day, result=JudgeStatus.ACCEPTED
            ).count()
            daily_submissions.append({
                "date": day.strftime("%Y-%m-%d"),
                "total": count,
                "accepted": ac,
            })

        return {
            "total": total,
            "accepted": ac_count,
            "global_ac_rate": global_ac_rate,
            "result_distribution": result_distribution,
            "language_distribution": language_distribution,
            "daily_submissions": daily_submissions,
        }

    def _get_recent_activity(self):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        now = timezone.now()

        # 修复：Submission 表没有 user 外键，只 select_related problem
        recent_submissions = Submission.objects.select_related("problem").order_by("-create_time")[:10]
        sub_list = []
        for s in recent_submissions:
            sub_list.append({
                "id": s.id,
                "username": s.username,      # 直接使用 username 字段
                "problem_id": s.problem._id,
                "problem_title": s.problem.title,
                "result": s.result,
                "language": s.language,
                "create_time": s.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        new_users_today = User.objects.filter(
            create_time__gte=today
        ).order_by("-create_time")[:10]
        user_list = []
        for u in new_users_today:
            user_list.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "create_time": u.create_time.strftime("%Y-%m-%d %H:%M:%S") if u.create_time else "",
            })

        recent_contests = Contest.objects.order_by("-create_time")[:5]
        contest_list = []
        for c in recent_contests:
            # 根据时间动态计算状态
            if c.start_time > now:
                status = "Not Started"
            elif c.end_time < now:
                status = "Ended"
            else:
                status = "Underway"
            contest_list.append({
                "id": c.id,
                "title": c.title,
                "status": status,
                "start_time": c.start_time.strftime("%Y-%m-%d %H:%M:%S") if c.start_time else "",
                "end_time": c.end_time.strftime("%Y-%m-%d %H:%M:%S") if c.end_time else "",
                "participant_count": c.acmcontestrank_set.count(),
            })

        return {
            "recent_submissions": sub_list,
            "new_users_today": user_list,
            "recent_contests": contest_list,
        }