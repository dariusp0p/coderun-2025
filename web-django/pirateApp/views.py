import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import HuntInstruction, PasswordGuess
from .oracle_client import fetch_next_direction, check_password, OracleAPIError


@require_http_methods(["GET"])
def index(request):
    return redirect("/compass/")


@require_http_methods(["GET", "POST"])
def compass(request):
    context = {
        "hunt_instructions": HuntInstruction.objects.order_by("instruction_id"),
        "error": None,
        "success": None,
    }

    if request.method == "POST":
        last_id_raw = (request.POST.get("last_id") or "").strip()

        if not last_id_raw.isdigit():
            context["error"] = "Instruction ID must be a non-negative integer."
            return render(request, "pirateApp/compass.html", context)

        last_id = int(last_id_raw)

        if last_id == 0:
            oracle_id = "set-sail"
            instruction_number = 1
        else:
            prev = HuntInstruction.objects.filter(instruction_id=last_id).first()
            if not prev:
                context["error"] = f"No instruction with ID={last_id} in DB."
                return render(request, "pirateApp/compass.html", context)

            oracle_id = (prev.raw_payload or {}).get("nextID")
            if not oracle_id:
                context["error"] = (
                    f"Instruction {last_id} has no nextID. Maybe you reached the end?"
                )
                return render(request, "pirateApp/compass.html", context)

            instruction_number = last_id + 1

        try:
            data = fetch_next_direction(oracle_id, instruction_number)
        except OracleAPIError as e:
            context["error"] = str(e)
            return render(request, "pirateApp/compass.html", context)

        obj, _ = HuntInstruction.objects.update_or_create(
            instruction_id=instruction_number,
            defaults={
                "title": data.get("title", ""),
                "direction": data.get("direction", ""),
                "distance_m": int(data.get("distanceInMeters", 0)),
                "description": data.get("instructionText", ""),
                "image_url": data.get("pictureUrl", ""),
                "raw_payload": data,
            },
        )

        context["success"] = (
            f"Fetched instruction #{obj.instruction_id}. "
            f"Next oracle_id is '{(data.get('nextID') or '')}'."
        )
        context["hunt_instructions"] = HuntInstruction.objects.order_by("instruction_id")

    return render(request, "pirateApp/compass.html", context)

@require_http_methods(["GET"])
def list_hunt_instructions(request):
    data = [
        {
            "instruction_id": h.instruction_id,
            "title": h.title,
            "direction": h.direction,
            "distanceInMeters": h.distance_m,
            "instructionText": h.description,
            "pictureUrl": h.image_url,
            "oracle_id": (h.raw_payload or {}).get("id"),
            "nextID": (h.raw_payload or {}).get("nextID"),
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
            {"error": "Trebuie sa trimiti instruction_number si oracle_id"},
            status=400
        )

    try:
        data = fetch_next_direction(str(oracle_id), int(instruction_number))
    except OracleAPIError as e:
        return JsonResponse({"error": str(e)}, status=400)

    obj, _ = HuntInstruction.objects.update_or_create(
        instruction_id=int(instruction_number),
        defaults={
            "title": data.get("title", ""),
            "direction": data.get("direction", ""),
            "distance_m": int(data.get("distanceInMeters", 0)),
            "description": data.get("instructionText", ""),
            "image_url": data.get("pictureUrl", ""),
            "raw_payload": data,
        },
    )

    return JsonResponse({
        "saved": True,
        "next_oracle_id": data.get("nextID"),
        "instruction": {
            "instruction_id": obj.instruction_id,
            "title": obj.title,
            "direction": obj.direction,
            "distanceInMeters": obj.distance_m,
            "description": obj.description,
            "pictureUrl": obj.image_url,
        }
    })


@require_http_methods(["GET", "POST"])
def treasure(request):
    context = {
        "result": None,
        "error": None,
        "guesses": PasswordGuess.objects.order_by("-created_at"),
    }

    if request.method == "POST":
        d1 = (request.POST.get("d1") or "").strip()
        d2 = (request.POST.get("d2") or "").strip()
        d3 = (request.POST.get("d3") or "").strip()
        d4 = (request.POST.get("d4") or "").strip()

        digits = [d1, d2, d3, d4]

        if not all(len(x) == 1 and x.isdigit() for x in digits):
            context["error"] = "All four fields must be single digits (0-9)."
            return render(request, "pirateApp/treasure.html", context)

        code = "".join(digits)

        try:
            data = check_password(code)
        except OracleAPIError as e:
            context["error"] = str(e)
            return render(request, "pirateApp/treasure.html", context)

        # Oracle gives only "message"
        message = data.get("message", str(data))

        PasswordGuess.objects.create(
            code=code,
            message=message,
            raw_payload=data,
        )

        context["result"] = {
            "code": code,
            "message": message,
        }
        context["guesses"] = PasswordGuess.objects.order_by("-created_at")

    return render(request, "pirateApp/treasure.html", context)
