from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Classification, ModeratorAction


CATEGORY_FILTERS = Classification.Category.choices
STATUS_ACTIONS = ["approved", "warned", "muted", "banned"]


def dashboard(request):
    queue = (
        Classification.objects.select_related("message")
        .filter(status=Classification.Status.PENDING)
        .order_by("-severity", "-created_at")
    )

    category = request.GET.get("category")
    if category:
        queue = queue.filter(category=category)

    min_severity = request.GET.get("min_severity")
    if min_severity:
        queue = queue.filter(severity__gte=int(min_severity))

    counts_by_category = (
        Classification.objects.filter(status=Classification.Status.PENDING)
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    queue = list(queue)
    for row in queue:
        row.tick_count = max(1, round(row.severity / 10))
        if row.severity >= 70:
            row.band = "high"
        elif row.severity >= 35:
            row.band = "med"
        else:
            row.band = "low"

    context = {
        "queue": queue,
        "category_choices": CATEGORY_FILTERS,
        "selected_category": category or "",
        "min_severity": min_severity or "",
        "counts_by_category": counts_by_category,
        "pending_total": Classification.objects.filter(status=Classification.Status.PENDING).count(),
        "resolved_total": Classification.objects.exclude(status=Classification.Status.PENDING).count(),
    }
    return render(request, "moderation/dashboard.html", context)


def history(request):
    actions = ModeratorAction.objects.select_related("classification__message", "moderator").order_by(
        "-created_at"
    )[:200]
    return render(request, "moderation/history.html", {"actions": actions})


@require_POST
def take_action(request, classification_id):
    classification = get_object_or_404(Classification, id=classification_id)
    new_status = request.POST.get("status")
    note = request.POST.get("note", "")

    if new_status not in STATUS_ACTIONS:
        return redirect("dashboard")

    ModeratorAction.objects.create(
        classification=classification,
        moderator=request.user if request.user.is_authenticated else None,
        previous_status=classification.status,
        new_status=new_status,
        note=note,
    )

    classification.status = new_status
    classification.save(update_fields=["status"])

    return redirect(request.META.get("HTTP_REFERER", "/"))
