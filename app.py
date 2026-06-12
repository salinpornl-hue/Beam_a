import streamlit as st
import math

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Beam Size Calculator", page_icon="🏗️")

st.title("🏗️ โปรแกรมประมาณการขนาดหน้าตัดคานเบื้องต้น")
st.markdown("โปรแกรมสำหรับคำนวณหน้าตัดคานสี่เหลี่ยมผืนผ้า (Simply Supported Beam) จากน้ำหนักแผ่กระจาย (Uniform Load)")

st.divider()

# ส่วนรับข้อมูล (Input)
st.header("📝 1. ป้อนข้อมูลการออกแบบ (Inputs)")
col1, col2 = st.columns(2)

with col1:
    L = st.number_input("ความยาวช่วงคาน L (เมตร)", min_value=0.1, value=4.0, step=0.5)
    w = st.number_input("น้ำหนักบรรทุก w (kg/m)", min_value=1.0, value=500.0, step=50.0)

with col2:
    sigma_allow = st.number_input(
        "หน่วยแรงดัดที่ยอมให้ (kg/cm²)", 
        min_value=1.0, value=100.0, 
        help="ตัวอย่าง: ไม้เนื้อแข็ง ~100-120, เหล็กรูปพรรณ ~1200-1400"
    )
    ratio = st.number_input("สัดส่วนความลึกต่อความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5)

# ส่วนคำนวณและแสดงผล
if st.button("🚀 คำนวณขนาดหน้าตัด", type="primary"):
    # 1. คำนวณ Max Bending Moment (kg-m)
    M_max = (w * L**2) / 8
    
    # แปลงหน่วยโมเมนต์จาก kg-m เป็น kg-cm
    M_max_cm = M_max * 100
    
    # 2. คำนวณ Required Section Modulus (cm^3)
    S_req = M_max_cm / sigma_allow
    
    # 3. คำนวณขนาดหน้าตัด b และ h (สมมติหน้าตัดสี่เหลี่ยม)
    # จากสูตร S = (b * h^2) / 6 โดย h = ratio * b
    # S = (ratio^2 * b^3) / 6 -> b = ขนรากที่ 3 ของ (6 * S) / ratio^2
    b = math.pow((6 * S_req) / (ratio**2), 1/3)
    h = ratio * b
    
    st.divider()
    
    # แสดงผล
    st.header("📊 2. ผลการคำนวณ (Outputs)")
    
    col_out1, col_out2 = st.columns(2)
    col_out1.metric(label="โมเมนต์ดัดสูงสุด (M_max)", value=f"{M_max:,.2f} kg-m")
    col_out2.metric(label="Section Modulus ที่ต้องการ (S_req)", value=f"{S_req:,.2f} cm³")
    
    st.subheader("📐 ขนาดหน้าตัดสี่เหลี่ยมที่แนะนำ")
    st.info(f"**ความกว้าง (b):** {b:.2f} ซม. ➡️ **แนะนำปัดเป็น {math.ceil(b)} ซม.**")
    st.info(f"**ความลึก (h):** {h:.2f} ซม. ➡️ **แนะนำปัดเป็น {math.ceil(h)} ซม.**")
    
    st.caption("หมายเหตุ: นี่เป็นการประเมินเบื้องต้นจากแรงดัด (Bending) เท่านั้น ในการออกแบบจริงต้องตรวจสอบแรงเฉือน (Shear) และระยะแอ่นตัว (Deflection) เพิ่มเติม")
