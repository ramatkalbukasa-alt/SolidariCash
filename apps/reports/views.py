from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib.auth.decorators import login_required

from apps.members.views import admin_required
from apps.cycles.models import Cycle
from apps.distributions.models import Distribution


@admin_required
def reports_index(request):
    cycles = Cycle.objects.all().order_by('-start_date')
    return render(request, 'reports/index.html', {'cycles': cycles})


@admin_required
def export_cycle_pdf(request, cycle_id):
    cycle = get_object_or_404(Cycle, pk=cycle_id)
    from .generators import generate_cycle_pdf
    buffer = generate_cycle_pdf(cycle)
    filename = f"solidaricash_{cycle.name.replace(' ', '_')}_rapport.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@admin_required
def export_cycle_excel(request, cycle_id):
    cycle = get_object_or_404(Cycle, pk=cycle_id)
    from .generators import generate_cycle_excel
    buffer = generate_cycle_excel(cycle)
    filename = f"solidaricash_{cycle.name.replace(' ', '_')}_rapport.xlsx"
    response = HttpResponse(
        buffer,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_receipt_pdf(request, distribution_id):
    distribution = get_object_or_404(Distribution, pk=distribution_id)
    if not request.user.is_admin and distribution.head.member.user != request.user:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Accès non autorisé.")
    from .generators import generate_member_receipt_pdf
    buffer = generate_member_receipt_pdf(distribution)
    filename = f"recu_distribution_{distribution.id}.pdf"
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
