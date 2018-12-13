import copy
import os
import zipfile
from ipaddress import ip_network

import dateutil.parser
from django.http import FileResponse
from django.conf import settings

from account.decorators import check_contest_permission, ensure_created_by
from account.models import User
from contest.models import ContestStatus
from problem.models import Problem
from submission.models import Submission, JudgeStatus
from utils.api import APIView, validate_serializer
from utils.cache import cache
from utils.constants import CacheKey
from utils.shortcuts import rand_str
from utils.tasks import delete_files
from ..models import Contest, ContestAnnouncement, ACMContestRank
from ..serializers import (ContestAnnouncementSerializer, ContestAdminSerializer,
                           CreateConetestSeriaizer, CreateContestAnnouncementSerializer,
                           EditConetestSeriaizer, EditContestAnnouncementSerializer,
                           ACMContesHelperSerializer, )
from account.decorators import super_admin_required


class ContestAPI(APIView):
    @validate_serializer(CreateConetestSeriaizer)
    def post(self, request):
        data = request.data
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        data["created_by"] = request.user
        if data["end_time"] <= data["start_time"]:
            return self.error("Start time must occur earlier than end time")
        if data.get("password") and data["password"] == "":
            data["password"] = None
        for ip_range in data["allowed_ip_ranges"]:
            try:
                ip_network(ip_range, strict=False)
            except ValueError:
                return self.error(f"{ip_range} is not a valid cidr network")
        contest = Contest.objects.create(**data)
        return self.success(ContestAdminSerializer(contest).data)

    @validate_serializer(EditConetestSeriaizer)
    def put(self, request):
        data = request.data
        try:
            contest = Contest.objects.get(id=data.pop("id"))
            ensure_created_by(contest, request.user)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        data["start_time"] = dateutil.parser.parse(data["start_time"])
        data["end_time"] = dateutil.parser.parse(data["end_time"])
        if data["end_time"] <= data["start_time"]:
            return self.error("Start time must occur earlier than end time")
        if not data["password"]:
            data["password"] = None
        for ip_range in data["allowed_ip_ranges"]:
            try:
                ip_network(ip_range, strict=False)
            except ValueError:
                return self.error(f"{ip_range} is not a valid cidr network")
        if not contest.real_time_rank and data.get("real_time_rank"):
            cache_key = f"{CacheKey.contest_rank_cache}:{contest.id}"
            cache.delete(cache_key)

        for k, v in data.items():
            setattr(contest, k, v)
        contest.save()
        return self.success(ContestAdminSerializer(contest).data)

    def get(self, request):
        contest_id = request.GET.get("id")
        if contest_id:
            try:
                contest = Contest.objects.get(id=contest_id)
                ensure_created_by(contest, request.user)
                return self.success(ContestAdminSerializer(contest).data)
            except Contest.DoesNotExist:
                return self.error("Contest does not exist")

        contests = Contest.objects.all().order_by("-create_time")
        if request.user.is_admin():
            contests = contests.filter(created_by=request.user)

        keyword = request.GET.get("keyword")
        if keyword:
            contests = contests.filter(title__contains=keyword)
        return self.success(self.paginate_data(request, contests, ContestAdminSerializer))


class ContestAnnouncementAPI(APIView):
    @validate_serializer(CreateContestAnnouncementSerializer)
    def post(self, request):
        """
        Create one contest_announcement.
        """
        data = request.data
        try:
            contest = Contest.objects.get(id=data.pop("contest_id"))
            ensure_created_by(contest, request.user)
            data["contest"] = contest
            data["created_by"] = request.user
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")
        announcement = ContestAnnouncement.objects.create(**data)
        return self.success(ContestAnnouncementSerializer(announcement).data)

    @validate_serializer(EditContestAnnouncementSerializer)
    def put(self, request):
        """
        update contest_announcement
        """
        data = request.data
        try:
            contest_announcement = ContestAnnouncement.objects.get(id=data.pop("id"))
            ensure_created_by(contest_announcement, request.user)
        except ContestAnnouncement.DoesNotExist:
            return self.error("Contest announcement does not exist")
        for k, v in data.items():
            setattr(contest_announcement, k, v)
        contest_announcement.save()
        return self.success()

    def delete(self, request):
        """
        Delete one contest_announcement.
        """
        contest_announcement_id = request.GET.get("id")
        if contest_announcement_id:
            if request.user.is_admin():
                ContestAnnouncement.objects.filter(id=contest_announcement_id,
                                                   contest__created_by=request.user).delete()
            else:
                ContestAnnouncement.objects.filter(id=contest_announcement_id).delete()
        return self.success()

    def get(self, request):
        """
        Get one contest_announcement or contest_announcement list.
        """
        contest_announcement_id = request.GET.get("id")
        if contest_announcement_id:
            try:
                contest_announcement = ContestAnnouncement.objects.get(id=contest_announcement_id)
                ensure_created_by(contest_announcement, request.user)
                return self.success(ContestAnnouncementSerializer(contest_announcement).data)
            except ContestAnnouncement.DoesNotExist:
                return self.error("Contest announcement does not exist")

        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Parameter error")
        contest_announcements = ContestAnnouncement.objects.filter(contest_id=contest_id)
        if request.user.is_admin():
            contest_announcements = contest_announcements.filter(created_by=request.user)
        keyword = request.GET.get("keyword")
        if keyword:
            contest_announcements = contest_announcements.filter(title__contains=keyword)
        return self.success(ContestAnnouncementSerializer(contest_announcements, many=True).data)


class ACMContestHelper(APIView):
    @check_contest_permission(check_type="ranks")
    def get(self, request):
        ranks = ACMContestRank.objects.filter(contest=self.contest, accepted_number__gt=0) \
            .values("id", "user__username", "user__userprofile__real_name", "submission_info")
        results = []
        for rank in ranks:
            for problem_id, info in rank["submission_info"].items():
                if info["is_ac"]:
                    results.append({
                        "id": rank["id"],
                        "username": rank["user__username"],
                        "real_name": rank["user__userprofile__real_name"],
                        "problem_id": problem_id,
                        "ac_info": info,
                        "checked": info.get("checked", False)
                    })
        results.sort(key=lambda x: -x["ac_info"]["ac_time"])
        return self.success(results)

    @check_contest_permission(check_type="ranks")
    @validate_serializer(ACMContesHelperSerializer)
    def put(self, request):
        data = request.data
        try:
            rank = ACMContestRank.objects.get(pk=data["rank_id"])
        except ACMContestRank.DoesNotExist:
            return self.error("Rank id does not exist")
        problem_rank_status = rank.submission_info.get(data["problem_id"])
        if not problem_rank_status:
            return self.error("Problem id does not exist")
        problem_rank_status["checked"] = data["checked"]
        rank.save(update_fields=("submission_info",))
        return self.success()


class DownloadContestSubmissions(APIView):
    def _dump_submissions(self, contest, exclude_admin=True):
        problem_ids = contest.problem_set.all().values_list("id", "_id")
        id2display_id = {k[0]: k[1] for k in problem_ids}
        ac_map = {k[0]: False for k in problem_ids}
        submissions = Submission.objects.filter(contest=contest, result=JudgeStatus.ACCEPTED).order_by("-create_time")
        user_ids = submissions.values_list("user_id", flat=True)
        users = User.objects.filter(id__in=user_ids)
        path = f"/tmp/{rand_str()}.zip"
        with zipfile.ZipFile(path, "w") as zip_file:
            for user in users:
                if user.is_admin_role() and exclude_admin:
                    continue
                user_ac_map = copy.deepcopy(ac_map)
                user_submissions = submissions.filter(user_id=user.id)
                for submission in user_submissions:
                    problem_id = submission.problem_id
                    if user_ac_map[problem_id]:
                        continue
                    file_name = f"{user.username}_{id2display_id[submission.problem_id]}.txt"
                    compression = zipfile.ZIP_DEFLATED
                    zip_file.writestr(zinfo_or_arcname=f"{file_name}",
                                      data=submission.code,
                                      compress_type=compression)
                    user_ac_map[problem_id] = True
        return path

    def get(self, request):
        contest_id = request.GET.get("contest_id")
        if not contest_id:
            return self.error("Parameter error")
        try:
            contest = Contest.objects.get(id=contest_id)
            ensure_created_by(contest, request.user)
        except Contest.DoesNotExist:
            return self.error("Contest does not exist")

        exclude_admin = request.GET.get("exclude_admin") == "1"
        zip_path = self._dump_submissions(contest, exclude_admin)
        delete_files.apply_async((zip_path,), countdown=300)
        resp = FileResponse(open(zip_path, "rb"))
        resp["Content-Type"] = "application/zip"
        resp["Content-Disposition"] = f"attachment;filename={os.path.basename(zip_path)}"
        return resp


class ContestCheckSimilarAPI(APIView):
    @super_admin_required
    def get(self, request):
        cid = request.GET.get("contest_id")
        contest = Contest.objects.get(id=cid)
        if contest.status != ContestStatus.CONTEST_ENDED:
            return self.error("Contest not ended")
        problems = Problem.objects.filter(contest_id=cid)
        owner = {}
        data_to_write = []

        for problem in problems:
            check_dir = os.path.join(settings.TEST_CASE_DIR, str(problem.id) + "_similar_tmp")
            if not os.path.exists(check_dir):
                os.mkdir(check_dir)
                os.chmod(check_dir, 0o710)

            submissions = Submission.objects.filter(problem_id=problem.id, result=JudgeStatus.ACCEPTED)
            for submission in submissions:
                owner[submission.id] = submission.username
                file_path = os.path.join(check_dir, submission.id)
                f = open(file_path, "w")
                f.write(submission.code)
                f.close()

            output_dir = os.path.join(check_dir, "result")
            check_files = check_dir + "/*"
            os.system(f"/app/sim_c -p -t40 -o {output_dir} {check_files}")
            f = open(output_dir)
            similar_submissions = []
            for line in f:
                # xxxx consists for xx % of xxxx material
                if "consists" in line:
                    splited_line = line.split()
                    sub1 = splited_line[0].split("/")[-1]
                    sub2 = splited_line[-2].split("/")[-1]
                    if owner[sub1] == owner[sub2]:
                        continue
                    similar_submissions.append(sub1)
                    similar_submissions.append(sub2)
                    sim = splited_line[3]
                    to_append = {
                        "problem_id": problem._id,
                        "submission_a": sub1,
                        "user_a": owner[sub1],
                        "submission_b": sub2,
                        "user_b": owner[sub2],
                        "similarity": sim
                    }
                    data_to_write.append(to_append)
            f.close()

            os.remove(output_dir)
            for submission in submissions:
                owner[submission.id] = submission.username
                file_path = os.path.join(check_dir, submission.id)
                os.remove(file_path)
                if submission.id in similar_submissions:
                    submission.shared = True
                    submission.save()
            os.rmdir(check_dir)

        contest.similarity_check_result = data_to_write
        contest.save()

        return self.success()
