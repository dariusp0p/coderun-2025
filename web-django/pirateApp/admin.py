from django.contrib import admin
from .models import HuntInstruction, PasswordGuess


@admin.register(HuntInstruction)
class HuntInstructionAdmin(admin.ModelAdmin):
    list_display = ("instruction_id", "title", "direction", "distance_nm", "created_at")
    search_fields = ("title", "direction", "instruction_id")
    ordering = ("instruction_id",)


@admin.register(PasswordGuess)
class PasswordGuessAdmin(admin.ModelAdmin):
    list_display = ("code", "is_correct", "created_at")
    ordering = ("-created_at",)