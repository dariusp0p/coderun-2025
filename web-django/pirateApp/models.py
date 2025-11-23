from django.db import models


class HuntInstruction(models.Model):
    instruction_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=200)
    direction = models.CharField(max_length=50)
    distance_m = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    raw_payload = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.instruction_id}] {self.title} - {self.distance_m} m {self.direction}"


class PasswordGuess(models.Model):
    code = models.CharField(max_length=4)
    message = models.TextField(blank=True)
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}"
