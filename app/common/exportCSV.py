from django.http import HttpResponse
import csv


def export_to_csv(modeladmin, request, queryset):
    app_name = modeladmin.model._meta.app_label
    model_name = modeladmin.model._meta.model_name
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = "attachment; filename={}_{}.csv".format(
        app_name, model_name)
    writer = csv.writer(response)

    # Escreva o cabeçalho CSV com os nomes das colunas
    writer.writerow([field.name for field in queryset.model._meta.fields])

    # Escreva os dados
    for obj in queryset:
        writer.writerow([getattr(obj, field.name)
                        for field in queryset.model._meta.fields])

    return response


export_to_csv.short_description = 'Exportar CSV'
