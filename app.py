import streamlit as st
import math

# ==========================================
# ตั้งค่าหน้าเว็บ (Page Configuration)
# ==========================================
st.set_page_config(page_title="Beam Size Calculator", page_icon="🏗️", layout="centered")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น")
st.markdown("คำนวณขนาดหน้าตัดคานสี่เหลี่ยมผืนผ้า (Simply Supported Beam) จากการรับน้ำหนักแผ่กระจาย พร้อมแสดงวิธีทำ")
st.divider()

# ==========================================
# 1. ส่วนรับข้อมูล (Inputs)
# ==========================================
st.header("📝 1. ป้อนข้อมูลการออกแบบ")

# แถวที่ 1: ข้อมูลคานและน้ำหนัก
col1, col2 = st.columns(2)
with col1:
    L = st.number_input("ความยาวช่วงคาน L (เมตร)", min_value=0.1, value=4.0, step=0.5)
with col2:
    w = st.number_input("น้ำหนักบรรทุกแผ่กระจาย w (kg/m)", min_value=1.0, value=500.0, step=50.0)

# แถวที่ 2: ข้อมูลวัสดุ
st.subheader("คุณสมบัติวัสดุและสัดส่วนหน้าตัด")

# ฐานข้อมูลวัสดุเบื้องต้น
material_dict = {
    "เหล็กรูปพรรณ (SS400)": 1200.0,
    "ไม้เนื้อแข็งมาก (เช่น ไม้เต็ง, ไม้แดง)": 120.0,
    "ไม้เนื้อแข็งปานกลาง (เช่น ไม้ตะแบก)": 90.0,
    "ไม้เนื้ออ่อน (เช่น ไม้ยาง)": 60.0,
    "กำหนดค่าเอง (Custom)": 0.0
}

col3, col4 = st.columns(2)
with col3:
    # เลือกประเภทวัสดุ
    selected_mat = st.selectbox("เลือกประเภทวัสดุของคาน", list(material_dict.keys()))
    
    # หากเลือก "กำหนดค่าเอง" ให้แสดงกล่องรับข้อความเพิ่ม
    if selected_mat == "กำหนดค่าเอง (Custom)":
        sigma_allow = st.number_input("ระบุหน่วยแรงดัดที่ยอมให้ (kg/cm²)", min_value=1.0, value=100.0)
    else:
        sigma_allow = material_dict[selected_mat]
        st.info(f"หน่วยแรงดัดที่ยอมให้ = **{sigma_allow}** kg/cm²")

with col4:
    ratio = st.number_input("สัดส่วน ความลึก ต่อ ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5)

# ==========================================
# 2. ส่วนคำนวณและแสดงผล (Calculation & Outputs)
# ==========================================
if st.button("🚀 คำนวณขนาดหน้าตัด", type="primary"):
    
    # --- กระบวนการคำนวณ ---
    M_max = (w * L**2) / 8          # โมเมนต์สูงสุด (kg-m)
    M_max_cm = M_max * 100          # แปลงเป็น kg-cm
    S_req = M_max_cm / sigma_allow  # Section Modulus (cm^3)
    
    # คำนวณ b และ h
    b_exact = math.pow((6 * S_req) / (ratio**2), 1/3)
    h_exact = ratio * b_exact
    
    # ปัดเศษขึ้นให้ทำงานได้จริง
    b_rounded = math.ceil(b_exact)
    h_rounded = math.ceil(h_exact)
    
    st.divider()
    
    # --- แสดงผลสรุป ---
    st.header("📊 2. สรุปผลการออกแบบหน้าตัด")
    
    c_out1, c_out2 = st.columns(2)
    c_out1.metric(label="โมเมนต์ดัดสูงสุด (M_max)", value=f"{M_max:,.2f} kg-m")
    c_out2.metric(label="Section Modulus ที่ต้องการ (S_req)", value=f"{S_req:,.2f} cm³")
    
    st.success(f"### 📐 ขนาดหน้าตัดที่แนะนำ: กว้าง {b_rounded} ซม. × ลึก {h_rounded} ซม.")
    st.caption(f"*(คำนวณได้จริง: b = {b_exact:.2f} ซม., h = {h_exact:.2f} ซม. ➡️ ทำการปัดเศษขึ้นเพื่อความปลอดภัย)*")
    
    st.divider()
    
    # --- แสดงวิธีทำอย่างละเอียด ---
    st.header("📖 3. วิธีการคำนวณ (Step-by-Step)")
    
    # ขั้นที่ 1
    st.subheader("ขั้นที่ 1: หาโมเมนต์ดัดสูงสุด (Maximum Bending Moment)")
    st.markdown("จากสูตรคานช่วงเดียวรับน้ำหนักแผ่กระจายสม่ำเสมอ (Simply Supported Beam with Uniform Load):")
    st.latex(r"M_{max} = \frac{w \cdot L^2}{8}")
    st.markdown("แทนค่า $w$ และ $L$:")
    st.latex(rf"M_{{max}} = \frac{{{w} \cdot {L}^2}}{{8}} = {M_max:,.2f} \text{{ kg-m}}")
    st.markdown("แปลงหน่วยเป็นกิโลกรัม-เซนติเมตร (kg-cm):")
    st.latex(rf"M_{{max}} = {M_max_cm:,.2f} \text{{ kg-cm}}")
    
    # ขั้นที่ 2
    st.subheader("ขั้นที่ 2: หาโมดูลัสหน้าตัดที่ต้องการ (Required Section Modulus)")
    st.markdown("จากสมการหน่วยแรงดัด $\sigma = \frac{M}{S}$ ย้ายข้างเพื่อหาค่า $S$:")
    st.latex(r"S_{req} = \frac{M_{max}}{\sigma_{allow}}")
    st.markdown("แทนค่า $M_{max}$ และ $\sigma_{allow}$:")
    st.latex(rf"S_{{req}} = \frac{{{M_max_cm:,.2f}}}{{{sigma_allow}}} = {S_req:,.2f} \text{{ cm}}^3")
    
    # ขั้นที่ 3
    st.subheader("ขั้นที่ 3: คำนวณขนาดหน้าตัด (กว้าง $b$ และ ลึก $h$)")
    st.markdown(f"กำหนดให้หน้าตัดเป็นรูปสี่เหลี่ยมผืนผ้า โดยมีสัดส่วน $h/b = {ratio}$ (นั่นคือ $h = {ratio}b$)")
    st.markdown("สูตรโมดูลัสหน้าตัดของสี่เหลี่ยม:")
    st.latex(r"S = \frac{b \cdot h^2}{6}")
    st.markdown("แทนค่า $h$ ลงในสมการและจัดรูปใหม่:")
    st.latex(rf"{S_req:,.2f} = \frac{{b \cdot ({ratio}b)^2}}{{6}} = \frac{{{ratio**2} \cdot b^3}}{{6}}")
    st.markdown("แก้สมการหาความกว้าง ($b$):")
    st.latex(rf"b = \sqrt[3]{{\frac{{{S_req:,.2f} \cdot 6}}{{{ratio**2}}}}} = {b_exact:.2f} \text{{ cm}}")
    st.markdown("หาความลึก ($h$):")
    st.latex(rf"h = {ratio} \cdot {b_exact:.2f} = {h_exact:.2f} \text{{ cm}}")
    
    # คำเตือนทางวิศวกรรม
    st.warning("⚠️ **หมายเหตุทางวิศวกรรม:** โปรแกรมนี้ออกแบบหน้าตัดโดยพิจารณาจาก **แรงดัด (Bending)** เพียงอย่างเดียว ในการใช้งานจริง วิศวกรจะต้องตรวจสอบแรงเฉือน (Shear) และระยะแอ่นตัว (Deflection) ร่วมด้วยเสมอ")
