import streamlit as st
import math
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Drip Irrigation Designer Pro", layout="wide")

st.title("🌱 Advanced Drip Irrigation Designer (Variable Field Boundary)")

# ========================= FIELD BOUNDARY INPUT =========================
st.sidebar.header("📐 Field Boundary")

length = st.sidebar.number_input("Field Length (m)", min_value=10.0, value=100.0)
width = st.sidebar.number_input("Field Width (m)", min_value=10.0, value=50.0)

# ========================= AGRONOMIC INPUTS  =========================
st.sidebar.header("🌳 Crop Layout")

tree_spacing_x = st.sidebar.number_input("Tree Spacing along row (m)", value=5.0)
tree_spacing_y = st.sidebar.number_input("Row spacing (m)", value=5.0)

drippers_per_tree = st.sidebar.number_input("Drippers per tree", value=4)
dripper_flow_lph = st.sidebar.number_input("Dripper flow (L/hr)", value=4.0)

# ========================= HYDRAULIC INPUTS =========================
st.sidebar.header("💧 Hydraulic Settings")

eff = st.sidebar.slider("Pump efficiency (%)", 50, 90, 70) / 100
zone_flow_limit = st.sidebar.number_input("Max zone flow (L/s)", value=5.0)

# ========================= COST INPUTS =========================
st.sidebar.header(" 💰 Cost Inputs")
pe_cost_per_m = st.sidebar.number_input("PE Pipe Cost ($/m)", value=1.5)
pvc_cost_per_m = st.sidebar.number_input("PVC Pipe Cost ($/m)", value=3.0)
valve_cost = st.sidebar.number_input("Valve Cost ($/unit)", value=25.0)
filter_cost = st.sidebar.number_input("Filter Cost ($/unit)", value=120.0)
fitting_factor = st.sidebar.slider("Fittings %", 5, 20, 10) / 100

# ========================= CALCULATIONS =========================
def hw(Q, D, L, C=140):
    return 10.67 * L * (Q ** 1.852) / ((C ** 1.852) * (D ** 4.871))


def pipe_size(Q):
    if Q < 0.5:
        return 0.016
    elif Q < 1.5:
        return 0.025
    elif Q < 3:
        return 0.032
    elif Q < 6:
        return 0.050
    else:
        return 0.075

# -------------------------  FIELD STRUCTURE -------------------------
trees_x = max(1, int(length / tree_spacing_x))
trees_y = max(1, int(width / tree_spacing_y))

total_trees = trees_x * trees_y
total_drippers = total_trees * drippers_per_tree

flow_lph = total_drippers * dripper_flow_lph
flow_m3s = flow_lph / 1000 / 3600
flow_ls = flow_lph / 3600

# ------------------------- ZONING -------------------------
zones = max(1, math.ceil(flow_ls / zone_flow_limit))
zone_flow = flow_ls / zones

# ========================= PIPE LENGTH CALCULATIONS (under modification to fit any selected design) =========================
# Laterals (Drip tubes, PE)
lateral_count = trees_y
lateral_length_total = lateral_count * length

# Submain or manifold (PVC)
submain_length_total = width

# Mainline (PVC)
main_length_total = length

# Add fittings factor
pe_total = lateral_length_total * (1 + fitting_factor)
pvc_total = (submain_length_total + main_length_total) * (1 + fitting_factor)
# ------------------------- FLOW DISTRIBUTION  -------------------------
emitters_per_lateral = trees_x * drippers_per_tree
lateral_full_flow_ls = (emitters_per_lateral * dripper_flow_lph) / 3600
lateral_avg_flow_ls = lateral_full_flow_ls * 0.35

# ------------------------- PIPE SIZING -------------------------
lateral_d = pipe_size(lateral_avg_flow_ls)
submain_d = pipe_size(zone_flow)
main_d = pipe_size(flow_ls)

# ------------------------- HEAD LOSS CALCULATION -------------------------
hf_lateral = hw(lateral_avg_flow_ls / 1000, lateral_d, length)
hf_submain = hw(zone_flow / 1000, submain_d, width)
hf_main = hw(flow_m3s, main_d, length)

static_head = 10
tdh = hf_lateral + hf_submain + hf_main + static_head

pump_kw = (flow_ls * tdh * 9.81) / (eff * 1000)

filters = max(1, int(flow_ls / 40))
fert_injector = flow_ls * 0.02
valves = zones
# ========================= COST ESTIMATION (Under modification) =========================
pe_cost = pe_total * pe_cost_per_m
pvc_cost = pvc_total * pvc_cost_per_m
valve_total_cost = valves * valve_cost
filter_total_cost = filters * filter_cost

total_cost = pe_cost + pvc_cost + valve_total_cost + filter_total_cost

# ========================= OUTPUT =========================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌳 Field Geometry")
    st.write(f"Field Size: {length} m × {width} m")
    st.write(f"Trees: {total_trees} ({trees_x} × {trees_y})")
    st.write(f"Drippers: {total_drippers}")
    st.write(f"Zones: {zones}")

with col2:
    st.subheader("💧 Flow System")
    st.write(f"Total Flow: {flow_ls:.2f} L/s")
    st.write(f"Zone Flow: {zone_flow:.2f} L/s")

st.subheader("🚰 Hydraulic Design")
st.write(f"Lateral loss: {hf_lateral:.2f} m")
st.write(f"Submain loss: {hf_submain:.2f} m")
st.write(f"Mainline loss: {hf_main:.2f} m")
st.write(f"Total Dynamic Head: {tdh:.2f} m")

st.subheader("🔄 Pump Design")
st.write(f"Pump Power: {pump_kw:.2f} kW")
st.write("Recommended: 1 duty + 1 standby pump")

st.subheader("🧪 Filtration & Fertigation")
st.write(f"Filters required: {filters}")
st.write(f"Fertilizer injector capacity: {fert_injector:.2f} L/s")

st.subheader("📦 Bill of Quantities")
st.write(f"PE Pipes (Laterals): {pe_total:.0f} m")
st.write(f"PVC Pipes (Main + Submain): {pvc_total:.0f} m")
st.write(f"Valves: {valves}")
st.write(f"Filters: {filters}")

st.subheader("💰 Cost Estimate")
st.write(f"PE Pipe Cost: ${pe_cost:.2f}")
st.write(f"PVC Pipe Cost: ${pvc_cost:.2f}")
st.write(f"Valves Cost: ${valve_total_cost:.2f}")
st.write(f"Filters Cost: ${filter_total_cost:.2f}")
st.write(f"Total Estimated Cost: ${total_cost:.2f}")

# ========================= VISUAL FIELD LAYOUT =========================
st.subheader("🗺️ Field Layout Visualization (under modification)")

fig, ax = plt.subplots()

# draw trees
for i in range(trees_x):
    for j in range(trees_y):
        ax.scatter(i * tree_spacing_x, j * tree_spacing_y, s=10)

# draw laterals
for j in range(trees_y):
    ax.plot([0, length], [j * tree_spacing_y, j * tree_spacing_y], linewidth=0.8)

ax.set_xlim(0, length)
ax.set_ylim(0, width)
ax.set_title("Drip Irrigation Layout")
ax.set_xlabel("Length (m)")
ax.set_ylabel("Width (m)")

st.pyplot(fig)

# =========================
# PDF REPORT
# =========================
def generate_pdf():
    file = "irrigation_report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("Drip Irrigation Design Report", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(f"Field: {length} x {width} m", styles["Normal"]))
    content.append(Paragraph(f"Trees: {total_trees}", styles["Normal"]))
    content.append(Paragraph(f"Flow: {flow_ls:.2f} L/s", styles["Normal"]))
    content.append(Paragraph(f"TDH: {tdh:.2f} m", styles["Normal"]))
    content.append(Paragraph(f"Pump Power: {pump_kw:.2f} kW", styles["Normal"]))
    content.append(Paragraph(f"Zones: {zones}", styles["Normal"]))

    doc.build(content)
    return file


st.subheader("📄 Export")

if st.button("Generate PDF Report"):
    file = generate_pdf()
    st.success("Report generated!")
    st.write(file)
