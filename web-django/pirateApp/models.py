from django.db import models


class HuntInstruction(models.Model):
    """
    Instrucțiuni venite din oracle (hard part).
    instruction_id e id-ul primit/folosit la API.
    """
    instruction_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=200)
    direction = models.CharField(max_length=50)
    distance_nm = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    raw_payload = models.JSONField(blank=True, null=True)  # păstrăm tot JSON-ul pentru debug/ending
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.instruction_id}] {self.title} - {self.distance_nm} nm {self.direction}"


class PasswordGuess(models.Model):
    code = models.CharField(max_length=4)  # ex: "0427"
    is_correct = models.BooleanField(default=False)
    message = models.TextField(blank=True)  # ce zice oracle
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} ({'OK' if self.is_correct else 'NO'})"
