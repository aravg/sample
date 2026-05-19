import os
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from config import PDF_OUTPUT_DIR


class TripPDFGenerator:
    BRAND_COLOR = colors.HexColor("#1E5F74")
    ACCENT_COLOR = colors.HexColor("#FFA62B")
    LIGHT_BG = colors.HexColor("#F0F8FF")
    DARK_TEXT = colors.HexColor("#1A1A2E")

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        self.styles.add(ParagraphStyle(
            "TitleStyle", parent=self.styles["Title"],
            fontSize=28, textColor=self.BRAND_COLOR, spaceAfter=8,
            alignment=TA_CENTER, fontName="Helvetica-Bold",
        ))
        self.styles.add(ParagraphStyle(
            "SubtitleStyle", parent=self.styles["Normal"],
            fontSize=14, textColor=self.ACCENT_COLOR, spaceAfter=4,
            alignment=TA_CENTER, fontName="Helvetica",
        ))
        self.styles.add(ParagraphStyle(
            "SectionHeader", parent=self.styles["Heading1"],
            fontSize=16, textColor=colors.white, spaceAfter=6, spaceBefore=12,
            fontName="Helvetica-Bold",
        ))
        self.styles.add(ParagraphStyle(
            "SubHeader", parent=self.styles["Heading2"],
            fontSize=13, textColor=self.BRAND_COLOR, spaceAfter=4,
            fontName="Helvetica-Bold",
        ))
        self.styles.add(ParagraphStyle(
            "BodyText2", parent=self.styles["Normal"],
            fontSize=10, spaceAfter=3, textColor=self.DARK_TEXT,
        ))
        self.styles.add(ParagraphStyle(
            "BulletText", parent=self.styles["Normal"],
            fontSize=10, leftIndent=12, bulletIndent=0, spaceAfter=2,
            textColor=self.DARK_TEXT,
        ))
        self.styles.add(ParagraphStyle(
            "CenterText", parent=self.styles["Normal"],
            fontSize=10, alignment=TA_CENTER, textColor=self.DARK_TEXT,
        ))

    def generate(self, trip_data: Dict[str, Any], filename: str = None) -> str:
        prefs = trip_data.get("trip_preferences", {})
        dest = prefs.get("destination", "Trip")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename or f"TripPlan_{dest.replace(' ', '_')}_{ts}.pdf"
        filepath = os.path.join(PDF_OUTPUT_DIR, filename)

        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )
        story = []
        story += self._cover_page(trip_data)
        story.append(PageBreak())
        story += self._trip_summary(trip_data)
        story += self._transport_section(trip_data)
        story += self._hotel_section(trip_data)
        story += self._weather_section(trip_data)
        story += self._itinerary_section(trip_data)
        story += self._budget_section(trip_data)
        story += self._places_section(trip_data)
        story += self._packing_checklist(trip_data)
        story += self._emergency_contacts(trip_data)
        story += self._footer_section()

        doc.build(story)
        return filepath

    def _section_header(self, title: str) -> list:
        header_table = Table(
            [[Paragraph(f"  {title}", self.styles["SectionHeader"])]],
            colWidths=[17*cm],
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), self.BRAND_COLOR),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.BRAND_COLOR]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ]))
        return [Spacer(1, 0.4*cm), header_table, Spacer(1, 0.3*cm)]

    def _cover_page(self, data: Dict) -> list:
        prefs = data.get("trip_preferences", {})
        profile = data.get("user_profile", {})
        elems = []
        elems.append(Spacer(1, 3*cm))
        elems.append(Paragraph("✈  AI TRIP PLANNER", self.styles["TitleStyle"]))
        elems.append(Spacer(1, 0.5*cm))
        dest = prefs.get("destination", "Your Destination")
        src = prefs.get("source", "Your City")
        elems.append(Paragraph(f"{src}  →  {dest}", self.styles["SubtitleStyle"]))
        elems.append(Spacer(1, 0.8*cm))
        elems.append(HRFlowable(width="100%", thickness=2, color=self.ACCENT_COLOR))
        elems.append(Spacer(1, 0.8*cm))

        cover_data = [
            ["Traveler", profile.get("name", "Valued Traveler")],
            ["Travel Type", prefs.get("travel_type", "N/A").capitalize()],
            ["Duration", f"{prefs.get('days', 'N/A')} days"],
            ["Travelers", str(prefs.get("travelers", 1))],
            ["Budget", f"₹{prefs.get('budget', 0):,.0f}"],
            ["Generated On", datetime.now().strftime("%d %B %Y")],
        ]
        t = Table(cover_data, colWidths=[6*cm, 10*cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), self.BRAND_COLOR),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.LIGHT_BG, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elems.append(t)
        elems.append(Spacer(1, 1*cm))
        elems.append(Paragraph(
            "Generated by AI Trip Planner | Powered by LangGraph Multi-Agent System",
            self.styles["CenterText"],
        ))
        return elems

    def _trip_summary(self, data: Dict) -> list:
        elems = self._section_header("TRIP SUMMARY")
        prefs = data.get("trip_preferences", {})
        plan = data.get("final_plan", {}) or {}

        summary_items = [
            ("Source", prefs.get("source", "N/A")),
            ("Destination", prefs.get("destination", "N/A")),
            ("Travel Dates", prefs.get("dates", {}).get("display", "N/A")),
            ("Trip Duration", f"{prefs.get('days', 'N/A')} days"),
            ("Number of Travelers", str(prefs.get("travelers", 1))),
            ("Travel Type", prefs.get("travel_type", "N/A").capitalize()),
            ("Total Budget", f"₹{prefs.get('budget', 0):,.0f}"),
        ]
        t = Table(summary_items, colWidths=[5*cm, 12*cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), self.BRAND_COLOR),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.LIGHT_BG, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        elems.append(t)

        if highlights := plan.get("highlights"):
            elems.append(Spacer(1, 0.3*cm))
            elems.append(Paragraph("Trip Highlights", self.styles["SubHeader"]))
            for h in highlights:
                elems.append(Paragraph(f"• {h}", self.styles["BulletText"]))
        return elems

    def _transport_section(self, data: Dict) -> list:
        elems = self._section_header("SECTION 1: FLIGHTS & TRANSPORT")
        transport = data.get("transport_data", {})
        if not transport:
            elems.append(Paragraph("Transport details not available.", self.styles["BodyText2"]))
            return elems

        if flights := transport.get("flights", {}).get("flights"):
            elems.append(Paragraph("Flight Options", self.styles["SubHeader"]))
            t_data = [["Airline", "Duration", "Price/Person", "Total Price"]]
            for f in flights[:3]:
                t_data.append([
                    f.get("airline", "N/A"),
                    f.get("duration", "N/A"),
                    f"₹{f.get('price_inr', 0):,.0f}",
                    f"₹{f.get('total_price_inr', 0):,.0f}",
                ])
            t = self._styled_table(t_data)
            elems.append(t)

        if trains := transport.get("trains", {}).get("trains"):
            elems.append(Spacer(1, 0.3*cm))
            elems.append(Paragraph("Train Options", self.styles["SubHeader"]))
            t_data = [["Train Name", "Number", "Duration", "Price/Person"]]
            for tr in trains[:3]:
                t_data.append([
                    tr.get("name", "N/A"),
                    tr.get("number", "N/A"),
                    tr.get("duration", "N/A"),
                    f"₹{tr.get('price_inr', 0):,.0f}",
                ])
            t = self._styled_table(t_data)
            elems.append(t)

        if rec := transport.get("recommendation"):
            elems.append(Spacer(1, 0.3*cm))
            elems.append(Paragraph(f"Recommendation: {rec}", self.styles["BodyText2"]))
        return elems

    def _hotel_section(self, data: Dict) -> list:
        elems = self._section_header("SECTION 2: HOTEL RECOMMENDATIONS")
        hotel = data.get("hotel_data", {})
        if not hotel:
            elems.append(Paragraph("Hotel details not available.", self.styles["BodyText2"]))
            return elems

        recs = hotel.get("recommendations", [])
        if recs:
            t_data = [["Hotel", "Area", "Stars", "Per Night", "Total", "Rating"]]
            for h in recs:
                t_data.append([
                    h.get("name", "N/A"),
                    h.get("area", "N/A"),
                    "★" * h.get("stars", 0),
                    f"₹{h.get('price_per_night', 0):,.0f}",
                    f"₹{h.get('total_cost_inr', 0):,.0f}",
                    str(h.get("rating", "N/A")),
                ])
            t = self._styled_table(t_data)
            elems.append(t)
            if best := hotel.get("best_pick"):
                elems.append(Spacer(1, 0.3*cm))
                elems.append(Paragraph(
                    f"Top Pick: {best.get('name')} — ₹{best.get('total_cost_inr', 0):,.0f} total",
                    self.styles["BodyText2"],
                ))
                if amenities := best.get("amenities"):
                    elems.append(Paragraph(
                        f"Amenities: {', '.join(amenities)}",
                        self.styles["BulletText"],
                    ))
        return elems

    def _weather_section(self, data: Dict) -> list:
        elems = self._section_header("WEATHER FORECAST")
        weather = data.get("weather_data", {})
        if not weather:
            elems.append(Paragraph("Weather data not available.", self.styles["BodyText2"]))
            return elems

        if summary := weather.get("summary"):
            elems.append(Paragraph(f"Overview: {summary}", self.styles["BodyText2"]))

        if forecasts := weather.get("forecasts"):
            t_data = [["Date", "Min °C", "Max °C", "Condition", "Humidity"]]
            for f in forecasts[:7]:
                t_data.append([
                    f.get("date", ""),
                    f"{f.get('temp_min', 0):.1f}",
                    f"{f.get('temp_max', 0):.1f}",
                    f.get("description", ""),
                    f"{f.get('humidity', 0)}%",
                ])
            t = self._styled_table(t_data)
            elems.append(t)
        return elems

    def _itinerary_section(self, data: Dict) -> list:
        elems = self._section_header("SECTION 3: DAY-WISE ITINERARY")
        itinerary = data.get("itinerary", {})
        if not itinerary:
            elems.append(Paragraph("Itinerary not generated.", self.styles["BodyText2"]))
            return elems

        days_data = itinerary.get("days", [])
        for day in days_data:
            day_num = day.get("day", "")
            title = day.get("title", f"Day {day_num}")
            elems.append(Spacer(1, 0.3*cm))
            day_header = Table(
                [[Paragraph(f"  Day {day_num}: {title}", self.styles["SubHeader"])]],
                colWidths=[17*cm],
            )
            day_header.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), self.LIGHT_BG),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]))
            elems.append(day_header)

            for activity in day.get("activities", []):
                time = activity.get("time", "")
                desc = activity.get("description", "")
                cost = activity.get("cost", "")
                cost_str = f" (₹{cost})" if cost else ""
                elems.append(Paragraph(
                    f"• <b>{time}</b> — {desc}{cost_str}",
                    self.styles["BulletText"],
                ))

            if food := day.get("food"):
                elems.append(Paragraph(
                    f"<i>Food: {food}</i>", self.styles["BulletText"]
                ))

        if tips := itinerary.get("tips"):
            elems.append(Spacer(1, 0.3*cm))
            elems.append(Paragraph("Travel Tips", self.styles["SubHeader"]))
            for tip in tips:
                elems.append(Paragraph(f"• {tip}", self.styles["BulletText"]))
        return elems

    def _budget_section(self, data: Dict) -> list:
        elems = self._section_header("SECTION 4: BUDGET REPORT")
        budget = data.get("budget_summary", {})
        if not budget:
            elems.append(Paragraph("Budget details not available.", self.styles["BodyText2"]))
            return elems

        prefs = data.get("trip_preferences", {})
        total_budget = prefs.get("budget", 0)
        breakdown = budget.get("breakdown", {})
        total = budget.get("total_inr", 0)

        if breakdown:
            t_data = [["Category", "Amount (₹)", "% of Total"]]
            for k, v in breakdown.items():
                pct = (v / total * 100) if total else 0
                t_data.append([k.replace("_", " ").title(), f"₹{v:,.0f}", f"{pct:.1f}%"])
            t_data.append(["TOTAL", f"₹{total:,.0f}", "100%"])
            t = self._styled_table(t_data)
            elems.append(t)

        elems.append(Spacer(1, 0.3*cm))
        status_color = colors.green if total <= total_budget else colors.red
        elems.append(Paragraph(
            f"Budget Status: {'Within Budget ✓' if total <= total_budget else 'Over Budget ✗'} "
            f"| Total: ₹{total:,.0f} / Allocated: ₹{total_budget:,.0f}",
            self.styles["BodyText2"],
        ))
        elems.append(Paragraph(
            f"Per Person: ₹{budget.get('per_person_inr', 0):,.0f}  |  "
            f"Daily Average: ₹{budget.get('daily_avg_inr', 0):,.0f}",
            self.styles["BodyText2"],
        ))

        if sug := budget.get("suggestions"):
            elems.append(Spacer(1, 0.2*cm))
            elems.append(Paragraph("Cost Saving Tips", self.styles["SubHeader"]))
            for s in sug:
                elems.append(Paragraph(f"• {s}", self.styles["BulletText"]))
        return elems

    def _places_section(self, data: Dict) -> list:
        elems = self._section_header("TOP ATTRACTIONS & EXPERIENCES")
        places = data.get("places_data", {})
        if not places:
            elems.append(Paragraph("Places data not available.", self.styles["BodyText2"]))
            return elems

        attractions = places.get("attractions", [])
        if attractions:
            t_data = [["Place", "Type", "Entry Fee", "Best Time"]]
            for p in attractions[:8]:
                fee = p.get("entry_fee")
                fee_str = f"₹{fee}" if fee else "Free"
                t_data.append([
                    p.get("name", "N/A"),
                    p.get("type", "N/A").capitalize(),
                    fee_str,
                    p.get("best_time", "Anytime"),
                ])
            t = self._styled_table(t_data)
            elems.append(t)

        if experiences := places.get("local_experiences"):
            elems.append(Spacer(1, 0.3*cm))
            elems.append(Paragraph("Local Experiences", self.styles["SubHeader"]))
            for exp in experiences:
                elems.append(Paragraph(f"• {exp}", self.styles["BulletText"]))
        return elems

    def _packing_checklist(self, data: Dict) -> list:
        elems = self._section_header("SECTION 5: PACKING CHECKLIST")
        prefs = data.get("trip_preferences", {})
        weather = data.get("weather_data", {})
        dest = prefs.get("destination", "").lower()
        summary = weather.get("summary", "").lower()

        base = [
            "✓ Valid government ID / Passport",
            "✓ Travel tickets (flights/trains)",
            "✓ Hotel booking confirmations",
            "✓ Travel insurance documents",
            "✓ Cash (₹) + Credit/Debit cards",
            "✓ Mobile charger + power bank",
            "✓ Personal medications",
        ]
        if any(k in dest for k in ["goa", "beach", "kerala"]):
            base += ["✓ Sunscreen SPF 50+", "✓ Swimwear", "✓ Beach towel", "✓ Sunglasses"]
        if any(k in dest for k in ["manali", "shimla", "leh", "ooty", "darjeeling"]):
            base += ["✓ Heavy jacket / down coat", "✓ Woollen cap & gloves", "✓ Thermal innerwear"]
        if "rain" in summary or "cloud" in summary:
            base += ["✓ Waterproof jacket / raincoat", "✓ Waterproof shoes"]

        cols = [base[:len(base)//2], base[len(base)//2:]]
        max_len = max(len(cols[0]), len(cols[1]))
        while len(cols[0]) < max_len:
            cols[0].append("")
        while len(cols[1]) < max_len:
            cols[1].append("")

        t_data = [[Paragraph(a, self.styles["BodyText2"]),
                   Paragraph(b, self.styles["BodyText2"])]
                  for a, b in zip(cols[0], cols[1])]
        t = Table(t_data, colWidths=[8.5*cm, 8.5*cm])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.LIGHT_BG, colors.white]),
        ]))
        elems.append(t)
        return elems

    def _emergency_contacts(self, data: Dict) -> list:
        elems = self._section_header("SECTION 6: EMERGENCY CONTACTS")
        contacts = [
            ["Police (National)", "100"],
            ["Ambulance (National)", "108"],
            ["Tourist Helpline", "1800-11-1363"],
            ["Women Helpline", "1091"],
            ["Fire", "101"],
        ]
        prefs = data.get("trip_preferences", {})
        dest = prefs.get("destination", "").lower()
        if "goa" in dest:
            contacts.append(["Goa Tourism", "+91-832-2226515"])
        elif "delhi" in dest:
            contacts.append(["Delhi Tourism", "+91-11-23361220"])
        contacts.append(["Travel Insurance Hotline", "Check your policy"])

        t = Table(contacts, colWidths=[10*cm, 7*cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), self.BRAND_COLOR),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [self.LIGHT_BG, colors.white]),
        ]))
        elems.append(t)
        return elems

    def _footer_section(self) -> list:
        elems = [
            Spacer(1, 0.5*cm),
            HRFlowable(width="100%", thickness=1, color=self.BRAND_COLOR),
            Spacer(1, 0.2*cm),
            Paragraph(
                "Generated by AI Trip Planner | LangGraph Multi-Agent System | "
                f"Report Date: {datetime.now().strftime('%d %B %Y')}",
                self.styles["CenterText"],
            ),
        ]
        return elems

    def _styled_table(self, data: list) -> Table:
        t = Table(data)
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), self.BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]
        t.setStyle(TableStyle(style))
        return t
