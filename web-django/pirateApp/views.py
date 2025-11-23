import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import HuntInstruction
from .oracle_client import fetch_next_direction, OracleAPIError


@require_http_methods(["GET"])
def list_hunt_instructions(request):
    data = [
        {
            "instruction_id": h.instruction_id,
            "title": h.title,
            "direction": h.direction,
            "distance_nm": h.distance_nm,
            "description": h.description,
            "image_url": h.image_url,
            "next_oracle_id": (h.raw_payload or {}).get("nextID")
        }
        for h in HuntInstruction.objects.order_by("instruction_id")
    ]
    return JsonResponse({"instructions": data})


@csrf_exempt
@require_http_methods(["POST"])
def fetch_and_save_instruction(request):
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "Body JSON invalid"}, status=400)

    instruction_number = body.get("instruction_number")
    oracle_id = body.get("oracle_id")

    if instruction_number is None or oracle_id is None:
        return JsonResponse(
            {"error": "Trebuie să trimiți instruction_number și oracle_id"},
            status=400
        )

    try:
        data = fetch_next_direction(oracle_id, int(instruction_number))
    except OracleAPIError as e:
        return JsonResponse({"error": str(e)}, status=400)

    obj, _ = HuntInstruction.objects.update_or_create(
        instruction_id=int(instruction_number),
        defaults={
            "title": data.get("title", ""),
            "direction": data.get("direction", ""),
            "distance_nm": int(data.get("distanceInMeters", 0)),  # păstrăm metri aici
            "description": data.get("instructionText", ""),
            "image_url": data.get("pictureUrl", ""),
            "raw_payload": data
        }
    )

    return JsonResponse({
        "saved": True,
        "next_oracle_id": data.get("nextID"),
        "instruction": {
            "instruction_id": obj.instruction_id,
            "title": obj.title,
            "direction": obj.direction,
            "distanceInMeters": obj.distance_nm,
            "description": obj.description,
            "pictureUrl": obj.image_url,
        }
    })
