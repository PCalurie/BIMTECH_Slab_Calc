import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from datetime import datetime
from PIL import Image as PILImage
import os
import tempfile
import math

# ============================
# ORIGINAL PDF GENERATOR (UNCHANGED)
# ============================
def generate_slab_pdf(name_client, beam_summary, total_num_beams, total_beam_length,
                      total_blocks, total_area, total_weight,
                      total_beam_cost, total_block_cost, grand_total):

    # save to a temporary file instead of a fixed phone path
    temp_dir = tempfile.mkdtemp()
    today = datetime.now().strftime("%Y-%m-%d")
    file_name = f"{name_client}Slab_Quotation{today}.pdf".replace(" ", "_")
    file_path = os.path.join(temp_dir, file_name)

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    title = styles["Title"]
    elements = []

    # Logo (same logic)
    logo_path = "C:/Users/a/Documents/Slab_Reports/bimtech-logo.jpeg"  # Keep your same logo file in same directory
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=500, height=70)
        elements.append(logo)
    else:
        st.warning("⚠️ Logo file not found at: " + logo_path)

    # Header
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Client:</b> {name_client}", normal))
    elements.append(Paragraph(f"<b>Date:</b> {today}", normal))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("<b>Supply of:</b>", normal))
    elements.append(Paragraph("> Eco-beams of 150mm × 50mm", normal))
    elements.append(Paragraph("> Eco-blocks of 120 × 200 × 400mm", normal))
    elements.append(Spacer(1, 10))

    # Beams Table
    table_data = [["Width (m)", "Beams (pcs)"]]
    for width, data in beam_summary.items():
        table_data.append([
            f"{width:.2f}", f"{data['num_beams']}"
        ])

    beam_table = Table(table_data, hAlign="LEFT", colWidths=[120, 120])
    beam_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")
    ]))
    elements.append(beam_table)
    elements.append(Spacer(1, 20))

    # Totals Section
    totals_table = [
        ["Total Beams:", f"{total_num_beams} pcs ({total_beam_length:.2f} m)"],
        ["Total Blocks:", f"{total_blocks:.0f} pcs (incl. 10% breakage)"],
        ["Total Area:", f"{total_area:,.2f} m²"],
        ["Total Weight:", f"{total_weight:.2f} tonnes"],
        ["Beams Cost @ 520:", f"KSh {total_beam_cost:,.2f}"],
        ["Blocks Cost @ 90:", f"KSh {total_block_cost:,.2f}"],
        ["Grand Total:", f"KSh {grand_total:,.2f}"],
    ]
    totals = Table(totals_table, hAlign="LEFT", colWidths=[200, 200])
    totals.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 6), (-1, 6), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 6), (-1, 6), colors.darkblue),
    ]))
    elements.append(Paragraph("<b>Summary Totals</b>", styles["Heading2"]))
    elements.append(totals)
    elements.append(Spacer(1, 15))

    # Footer
    elements.append(Paragraph("> PAYMENT: Equity Bank ACC...", normal))
    elements.append(Paragraph("> RECOMMENDED: BRC A142/98 & CONCRETE CLASS 25", normal))
    elements.append(Paragraph("> TRANSPORT NOT INCLUDED", normal))
    elements.append(Paragraph("> WE PROVIDE ONE TECHNICIAN FOR SUPERVISION", normal))
    elements.append(Paragraph("> QUOTATION VALID FOR ONE MONTH", normal))
    elements.append(Spacer(1, 10))
    footer = Paragraph("<i>Thank you for choosing BIMTECH! We value your business.</i>", normal)
    elements.append(footer)

    doc.build(elements)
    return file_path


# ============================
# CALCULATION LOGIC
# ============================
def calculate_slabs_summary(client_name, room_data):
    BEAM_COST_PER_M = 520
    BLOCK_COST = 90
    BEAM_SPAN = 0.15
    BLOCK_SPAN = 0.4
    BLOCK_LENGTH = 0.2
    BEAM_SPACING = BEAM_SPAN + BLOCK_SPAN

    total_blocks = 0
    total_unbroken = 0
    total_beam_cost = 0
    total_block_cost = 0
    total_beam_length = 0
    total_num_beams = 0
    total_area = 0
    total_weight = 0
    beam_summary = {}

    for room in room_data:
        width = room['width']
        length = room['length']

        beam_length = width
        extra_beam = 0
        gap_end = length % BEAM_SPACING
        area = width * length

        extra_block_layer = 0
        if 0.2 <= gap_end <= 0.4:
            extra_block_layer = 1
        elif 0.4 < gap_end < BEAM_SPACING:
            extra_beam = 1

        blocks_per_beam = int(width // BLOCK_LENGTH)
        num_beams = int(length // BEAM_SPACING) + extra_beam
        num_beams_blocks = (num_beams - 1)
        total_blocks_room = (blocks_per_beam * num_beams_blocks) + (extra_block_layer * blocks_per_beam)
        total_unbroken += total_blocks_room
        breakage = math.ceil(total_unbroken * 0.1)
        total_blocks = total_unbroken + breakage

        beam_cost_room = num_beams * beam_length * BEAM_COST_PER_M
        weight_blocks = total_blocks_room * 15
        weight_beams = (num_beams * beam_length) * 18

        total_beam_length += num_beams * beam_length
        total_num_beams += num_beams
        total_beam_cost += beam_cost_room
        total_block_cost = total_blocks * BLOCK_COST
        total_area += area
        total_weight += (weight_beams + weight_blocks) / 1000

        width_key = round(width + 0, 1)
        if width_key not in beam_summary:
            beam_summary[width_key] = {"num_beams": 0, "total_length": 0}
        beam_summary[width_key]["num_beams"] += num_beams
        beam_summary[width_key]["total_length"] += num_beams * beam_length

    extra_weight = (breakage * 14) / 1000
    total_weight += extra_weight
    grand_total = total_beam_cost + total_block_cost

    return (
        client_name,
        beam_summary,
        total_num_beams,
        total_beam_length,
        total_blocks,
        total_area,
        total_weight,
        total_beam_cost,
        total_block_cost,
        grand_total
    )


# ============================
# STREAMLIT INTERFACE
# ============================
letterhead = PILImage.open("bimtech-logo.jpeg")
st.image(letterhead, width="stretch")

st.markdown(
    "<h3 style='text-align:center; color:#003366;'>Eco-Slab Quotation System</h3>",
    unsafe_allow_html=True
)


name_client = st.text_input("Enter Client Name", "LOGO")
num_rooms = st.number_input("Enter number of rooms", min_value=1, value=1, step=1)

room_data = []
for i in range(num_rooms):
    st.markdown(f"### Room {i+1}")
    width = st.number_input(f"Width of Room {i+1} (m)", min_value=0.1, step=0.1, key=f"w{i}")
    length = st.number_input(f"Length of Room {i+1} (m)", min_value=0.1, step=0.1, key=f"l{i}")
    room_data.append({"width": width, "length": length})

if st.button("🧮 Calculate & Generate Quotation"):
    results = calculate_slabs_summary(name_client, room_data)
    (
        name_client,
        beam_summary,
        total_num_beams,
        total_beam_length,
        total_blocks,
        total_area,
        total_weight,
        total_beam_cost,
        total_block_cost,
        grand_total
    ) = results

    st.success("✅ Calculation Completed Successfully!")
    st.write("### Summary Totals")
    st.write(f"*Total Beams:* {total_num_beams} pcs ({total_beam_length:.2f} m)")
    st.write(f"*Total Blocks:* {total_blocks:.0f} pcs (incl. 10% breakage)")
    st.write(f"*Total Area:* {total_area:.2f} m²")
    st.write(f"*Total Weight:* {total_weight:.2f} tonnes")
    st.write(f"*Beams Cost:* KSh {total_beam_cost:,.2f}")
    st.write(f"*Blocks Cost:* KSh {total_block_cost:,.2f}")
    st.write(f"*Grand Total:* 💰 KSh {grand_total:,.2f}")

    # Generate PDF
    pdf_path = generate_slab_pdf(
        name_client, beam_summary, total_num_beams, total_beam_length,
        total_blocks, total_area, total_weight, total_beam_cost, total_block_cost, grand_total
    )

    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="📄 Download Quotation PDF",
            data=pdf_file,
            file_name=os.path.basename(pdf_path),
            mime="application/pdf"
        )