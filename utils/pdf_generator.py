from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_trip_pdf(trip, budget, activities):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    x = 50
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, f"Trip Plan — {trip.destination}")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(x, y, f"Dates: {trip.start_date} → {trip.end_date}")
    y -= 18
    c.drawString(x, y, f"Travelers: {trip.travelers}")
    y -= 20

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Budget Breakdown")
    y -= 18
    c.setFont("Helvetica", 11)
    for key in ("hotel","food","transport","activities","misc","total"):
        c.drawString(x, y, f"{key.capitalize()}: {budget.get(key)}")
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x, y, "Activities")
    y -= 18
    c.setFont("Helvetica", 11)
    for a in activities:
        if y < 60:
            c.showPage()
            y = height - 50
        c.drawString(x, y, f"- {a.activity_name} ( ${a.cost} )")
        y -= 14

    c.showPage()
    c.save()
    buf.seek(0)
    return buf
