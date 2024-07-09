from django.db import models
from django.contrib.postgres.fields import ArrayField
from posthog.models.utils import UUIDModel
from django.db import transaction


class ErrorTrackingGroup(UUIDModel):
    class Status(models.TextChoices):
        ARCHIVED = "archived", "Archived"
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"
        PENDING_RELEASE = "pending_release", "Pending release"

    team: models.ForeignKey = models.ForeignKey("Team", on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, blank=True)
    fingerprint: models.CharField = models.CharField(max_length=200, null=False, blank=False)
    merged_fingerprints: ArrayField = ArrayField(models.CharField(max_length=200, null=False), default=list)
    status: models.CharField = models.CharField(
        max_length=40, choices=Status.choices, default=Status.ACTIVE, null=False
    )
    assignee: models.ForeignKey = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    @transaction.atomic
    def merge(self, groups: list["ErrorTrackingGroup"]) -> None:
        if not groups:
            return

        merged_fingerprints = set(self.merged_fingerprints)
        for group in groups:
            fingerprints = [group.fingerprint, *group.merged_fingerprints]
            merged_fingerprints |= set(fingerprints)

        self.merged_fingerprints = list(merged_fingerprints)
        self.save()

        for group in groups:
            group.delete()
