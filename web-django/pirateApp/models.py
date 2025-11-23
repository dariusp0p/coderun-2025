from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Instruction(models.Model):
    DIRECTION_CHOICES = [
        ('east', 'East'),
        ('west', 'West'),
        ('south', 'South'),
        ('north', 'North'),
        ('north-east', 'North-East'),
        ('north-west', 'North-West'),
        ('south-east', 'South-East'),
        ('south-west', 'South-West'),
    ]

    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    distance_nm = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    description = models.CharField(max_length=255)
    previous_instruction = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='next_instructions'
    )
    risk_level = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.distance_nm} miles {self.direction}"


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
