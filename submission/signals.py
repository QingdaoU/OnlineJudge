# submission/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from submission.models import Submission
from submission.tasks import sync_submission_to_neo4j

@receiver(post_save, sender=Submission)
def submission_post_save(sender, instance, created, **kwargs):
    # 只在新创建时同步（更新时通常不会改变图谱关系，如需同步更新可去除 created 判断）
    if created:
        sync_submission_to_neo4j.send(str(instance.id))