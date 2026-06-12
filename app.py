import streamlit as st
import math

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Beam Size Calculator", page_icon="🏗️")

st.title("🏗️ โปรแกรมประมาณการขนาดหน้าตัดคานเบื้องต้น")
st.markdown("คำนวณหน้าตัดคานสี่เหลี่ยมผืนผ้า (Simply Supported Beam) พร้อมแสดงวิธีทำอย่างละเอียด")

st.divider()

# ---------------------------------------------
# 1. ส่วนรับข้อมูล (Input)
# ---------------------------------------------
st.header("📝 1. ป้อนข้อมูลการออกแบบ (Inputs)")
col1, col2 = st.columns(2)

with col1:
    L = st.number_input("ความยาวช่วงคาน L (เมตร)", min_value=0.1, value=4.0, step=0.5)
    w = st.number_input("น้ำหนักบรรทุกแผ่กระจาย w (kg/m)", min_value=1.0, value=500.0, step=50.0)

with col2:
    sigma_allow = st.number_input(
        "หน่วยแรงดัดที่ยอมให้ (kg/cm²)", 
        min_value=1.0, value=100.0, 
        help="ตัวอย่าง: ไม้เนื้อแข็ง ~100-120, เหล็กรูปพรรณ ~1200-1400"
    )
    ratio = st.number_input("สัดส่วนความลึกต่อความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5)

# ---------------------------------------------
# 2. ส่วนคำนวณและแสดงผล (Calculation & Output)
# ---------------------------------------------
if st.button("🚀 คำนวณขนาดหน้าตัดพร้อมแสดงวิธีทำ", type="primary"):
    
    # --- เริ่มการคำนวณ ---
    M_max = (w * L**2) / 8          # kg-m
    M_max_cm = M_max * 100          # kg-cm
    S_req = M_max_cm / sigma_allow  # cm^3
    
    # b = รากที่ 3 ของ (6 * S_req) / ratio^2
    b = math.pow((6 * S_req) / (ratio**2), 1/3)
    h = ratio * b
    
    st.divider()
    
    # --- แสดงผลสรุป ---
    st.header("📊 2. สรุปผลการคำนวณ")
    
    col_out1, col_out2 = st.columns(2)
    col_out1.metric(label="โมเมนต์ดัดสูงสุด (M_max)", value=f"{M_max:,.2f} kg-m")
    col_out2.metric(label="Section Modulus ที่ต้องการ (S_req)", value=f"{S_req:,.2f} cm³")
    
    st.success(f"**ขนาดหน้าตัดสี่เหลี่ยมที่แนะนำ:** กว้าง {math.ceil(b)} ซม. × ลึก {math.ceil(h)} ซม.")
    
    st.divider()
    
    # --- แสดงวิธีทำอย่างละเอียด (Step-by-Step) ---
    st.header("📖 3. แสดงวิธีทำ (Step-by-Step Calculation)")
    
    # ขั้นที่ 1
    st.subheader("ขั้นที่ 1: คำนวณโมเมนต์ดัดสูงสุด (Maximum Bending Moment)")
    st.markdown("จากสูตรคานช่วงเดียวรับน้ำหนักแผ่กระจายสม่ำเสมอเต็มช่วง (Simply Supported Beam with Uniform Load):")
    st.latex(r"M_{max} = \frac{w \cdot L^2}{8}")
    st.markdown("แทนค่า:")
    st.latex(rf"M_{{max}} = \frac{{{w} \cdot {L}^2}}{{8}} = {M_max:,.2f} \text{{ kg-m}}")
    st.markdown("แปลงหน่วยเป็น **kg-cm** (คูณ 100):")
    st.latex(rf"M_{{max}} = {M_max_cm:,.2f} \text{{ kg-cm}}")
    
    # ขั้นที่ 2
    st.subheader("ขั้นที่ 2: คำนวณโมดูลัสหน้าตัดที่ต้องการ (Required Section Modulus)")
    st.markdown("จากสมการหน่วยแรงดัด $\sigma = \frac{M}{S}$ ย้ายข้างสมการจะได้:")
    st.latex(r"S_{req} = \frac{M_{max}}{\sigma_{allow}}")
    st.markdown("แทนค่า:")
    st.latex(rf"S_{{req}} = \frac{{{M_max_cm:,.2f}}}{{{sigma_allow}}} = {S_req:,.2f} \text{{ cm}}^3")
    
    # ขั้นที่ 3
    st.subheader("ขั้นที่ 3: หาขนาดหน้าตัด (กว้าง $b$ และ ลึก $h$)")
    st.markdown(f"กำหนดให้สัดส่วนความลึกต่อความกว้าง $h/b = {ratio}$ ดังนั้น $h = {ratio}b$")
    st.markdown("จากสูตรโมดูลัสหน้าตัดของสี่เหลี่ยมผืนผ้า:")
    st.latex(r"S = \frac{b \cdot h^2}{6}")
    st.markdown("แทนค่า $h$ ลงในสมการ:")
    st.latex(rf"{S_req:,.2f} = \frac{{b \cdot ({ratio}b)^2}}{{6}} = \frac{{{ratio**2} \cdot b^3}}{{6}}")
    st.markdown("แก้สมการหาค่า $b$ (ความกว้าง):")
    st.latex(rf"b^3 = \frac{{{S_req:,.2f} \cdot 6}}{{{ratio**2}}}")
    st.latex(rf"b = \sqrt[3]{{{(S_req * 6) / (ratio**2):,.2f}}} = {b:.2f} \text{{ cm}}")
    st.markdown("หาค่า $h$ (ความลึก):")
    st.latex(rf"h = {ratio} \cdot {b:.2f} = {h:.2f} \text{{ cm}}")
    
    st.info("💡 **ข้อแนะนำ:** ในทางปฏิบัติเรามักจะปัดตัวเลขขึ้นเพื่อให้ทำงานได้จริงและมีความปลอดภัยเพิ่มขึ้น")
