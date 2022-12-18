from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def pdf_create(ingredients):
    pdfmetrics.registerFont(
        TTFont('TNR', 'times.ttf', 'UTF-8')
    )
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        'attachment; filename="shopping_list.pdf"'
    )
    page = canvas.Canvas(response, pagesize=A4)
    page.setFont('TNR', size=24)
    page.setTitle('Список покупок')
    page.drawString(200, 800, 'Список покупок')
    page.setFont('TNR', size=16)
    height = 750
    for i, j in enumerate(ingredients, 1):
        page.drawString(75, height, (
            f'{i}) {j ["ingredient__name"]} - '
            f'{j ["total_ingredients"]}'
            f'{j ["ingredient__measurement_unit"]}'
        ))
        height -= 25
    page.showPage()
    page.save()
    return response
