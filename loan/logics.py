import io
import mimetypes
from django.http import FileResponse

from weasyprint import HTML


def return_pdf(html_content, filename):
    buffer = io.BytesIO()
    html = HTML(string=html_content)
    html.write_pdf(buffer)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=False, content_type="application/pdf", filename=f"{filename}.pdf")