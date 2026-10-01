"""One-page downloadable forecast report for TaxLens AI."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


NAVY = HexColor("#17233B")
BLUE = HexColor("#5278A5")
CORAL = HexColor("#F47C6C")
LAVENDER = HexColor("#DDD7F4")
CREAM = HexColor("#F7F3EA")
PAPER = HexColor("#FFFCF7")
MUTED = HexColor("#667085")
LINE = HexColor("#DCD8D0")


def _money(value: float) -> str:
    return f"$ {value:,.0f}"


def _card(pdf: canvas.Canvas, x: float, y: float, width: float, label: str, value: str) -> None:
    pdf.setFillColor(PAPER)
    pdf.setStrokeColor(LINE)
    pdf.roundRect(x, y, width, 62, 12, fill=1, stroke=1)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(x + 13, y + 41, label.upper())
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x + 13, y + 17, value)


def _row(pdf: canvas.Canvas, x: float, y: float, label: str, value: str, width: float) -> None:
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(x, y, label)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawRightString(x + width, y, value)
    pdf.setStrokeColor(LINE)
    pdf.line(x, y - 8, x + width, y - 8)


def build_forecast_pdf(
    *,
    inputs,
    result,
    impact: dict,
    indiana_result,
    state: str,
    county: str,
    income_profile: str,
) -> bytes:
    """Return a polished one-page PDF containing the active forecast."""
    local_balance = (
        indiana_result.combined_refund_or_amount_owed
        if indiana_result is not None
        else 0.0
    )
    combined_balance = result.refund_or_amount_owed + local_balance
    is_refund = combined_balance >= 0
    outlook = (
        "CLEAR SKIES"
        if combined_balance > 250
        else "CLOUDY"
        if combined_balance >= -250
        else "STORM WARNING"
    )
    balance_label = "Projected refund cushion" if is_refund else "Projected amount owed"
    location_tax = (
        indiana_result.estimated_state_tax + indiana_result.estimated_county_tax
        if indiana_result is not None
        else 0.0
    )
    location_payments = (
        indiana_result.projected_state_withholding
        + indiana_result.projected_county_withholding
        if indiana_result is not None
        else 0.0
    )
    total_payments = result.projected_payments + location_payments
    per_check = (
        abs(combined_balance) / inputs.remaining_paychecks
        if combined_balance < 0 and inputs.remaining_paychecks > 0
        else 0.0
    )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("TaxLens 2026 Forecast")
    pdf.setAuthor("TaxLens AI")
    page_width, page_height = letter

    pdf.setFillColor(CREAM)
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    # Header
    pdf.setFillColor(NAVY)
    pdf.roundRect(34, 674, 544, 84, 20, fill=1, stroke=0)
    pdf.setFillColor(CORAL)
    pdf.roundRect(52, 711, 29, 29, 8, fill=1, stroke=0)
    pdf.setFillColor(PAPER)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(66.5, 720, "TL")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(92, 719, "TaxLens AI")
    pdf.setFillColor(LAVENDER)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(92, 701, "YOUR 2026 YEAR-END FORECAST")
    pdf.setFillColor(PAPER)
    pdf.setFont("Helvetica", 9)
    location = f"{county} County, Indiana" if state == "Indiana" else state
    pdf.drawRightString(558, 720, location)
    pdf.drawRightString(558, 703, f"{inputs.filing_status}  |  {income_profile}")

    # Outlook
    pdf.setFillColor(PAPER)
    pdf.setStrokeColor(LINE)
    pdf.roundRect(34, 548, 544, 108, 18, fill=1, stroke=1)
    pdf.setFillColor(CORAL if not is_refund else BLUE)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(54, 628, f"TAX WEATHER  /  {outlook}")
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 34)
    pdf.drawString(52, 584, _money(abs(combined_balance)))
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 11)
    pdf.drawString(54, 563, balance_label)
    pdf.setFillColor(LAVENDER)
    pdf.circle(512, 602, 34, fill=1, stroke=0)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(512, 594, "OK" if is_refund else "!")

    # Key figures
    gap = 10
    card_width = (544 - gap * 2) / 3
    _card(pdf, 34, 466, card_width, "Projected wages", _money(result.projected_wages))
    _card(pdf, 34 + card_width + gap, 466, card_width, "Federal tax", _money(result.projected_total_tax))
    reserve_value = f"{impact['reserve_rate']:.0%}" if result.side_gig_net_profit > 0 else "N/A"
    _card(pdf, 34 + (card_width + gap) * 2, 466, card_width, "Side-income reserve", reserve_value)

    # Breakdown and suggested action
    pdf.setFillColor(PAPER)
    pdf.setStrokeColor(LINE)
    pdf.roundRect(34, 274, 264, 172, 16, fill=1, stroke=1)
    pdf.roundRect(314, 274, 264, 172, 16, fill=1, stroke=1)
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, 420, "Forecast breakdown")
    pdf.drawString(330, 420, "What to know")
    _row(pdf, 50, 393, "Federal taxable income", _money(result.taxable_income), 232)
    _row(pdf, 50, 366, "Federal payments", _money(result.projected_payments), 232)
    _row(pdf, 50, 339, "State and county tax", _money(location_tax), 232)
    _row(pdf, 50, 312, "Total projected payments", _money(total_payments), 232)

    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 9)
    if combined_balance < 0 and inputs.remaining_paychecks > 0:
        pdf.drawString(330, 392, "Approximate gap per remaining paycheck")
        pdf.setFillColor(CORAL)
        pdf.setFont("Helvetica-Bold", 22)
        pdf.drawString(330, 361, _money(per_check))
    elif combined_balance < 0:
        pdf.drawString(330, 392, "The forecast currently shows an amount owed.")
    else:
        pdf.drawString(330, 392, "Projected payments currently exceed the estimate.")
    if result.side_gig_net_profit > 0:
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(330, 329, "Projected net side income")
        pdf.setFillColor(NAVY)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(330, 307, _money(result.side_gig_net_profit))
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(330, 288, f"Suggested reserve: {impact['reserve_rate']:.0%} of net side income")
    else:
        pdf.setFillColor(MUTED)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(330, 329, "No side income is included in this forecast.")

    # Scope
    pdf.setFillColor(NAVY)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(34, 243, "About this estimate")
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(34, 222, "Includes 2026 federal brackets, the standard deduction, self-employment tax, and selected adjustments.")
    if indiana_result is not None:
        pdf.drawString(34, 207, f"Also includes a simplified Indiana and {county} County estimate.")
    else:
        pdf.drawString(34, 207, "State tax is not included for the selected location.")
    pdf.drawString(34, 192, "Does not include every credit, deduction, penalty, capital gain, or special tax situation.")

    # Footer
    pdf.setStrokeColor(LINE)
    pdf.line(34, 158, 578, 158)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 7.5)
    pdf.drawString(34, 137, "Educational estimate only. TaxLens does not prepare or file tax returns and does not provide tax advice.")
    pdf.drawString(34, 123, "Assumptions reviewed September 30, 2026. Verify important decisions with official resources or a tax professional.")
    pdf.setFillColor(CORAL)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawRightString(578, 137, "TAXLENS AI")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
