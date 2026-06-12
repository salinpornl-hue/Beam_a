import streamlit as st
import math

# ==========================================
# ตั้งค่าหน้าเว็บ (Page Configuration)
# ==========================================
st.set_page_config(page_title="Beam Design Calculator", page_icon="🏗️", layout="wide")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น")
st.markdown("รองรับการคำนวณน้ำหนักแบบแผ่กระจาย (Uniform Load) และแบบจุด (Point Load)")
st.divider()

# สร้าง Tabs สำหรับแยกประเภทคาน
tab1, tab2 = st.tabs(["🪵 เหล็กรูปพรรณ / ไม้ (Homogeneous)", "🧱 คอนกรีตเสริมเหล็ก (RC Beam)"])

# ==========================================
# TAB 1: เหล็กรูปพรรณ และ ไม้
# ==========================================
with tab1:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (เหล็ก/ไม้)")
    
    col1, col2 = st.columns(2)
    with col1:
        L_homo = st.number_input("ความยาวช่วงคาน L (เมตร)", min_value=0.1, value=4.0, step=0.5, key="L_homo")
        
        # เลือกประเภทน้ำหนักบรรทุก
        load_type_homo = st.radio("รูปแบบน้ำหนักบรรทุก", ["น้ำหนักแผ่กระจาย (Uniform Load)", "น้ำหนักกระทำเป็นจุดกึ่งกลาง (Point Load)"], key="load_homo")
        if "Uniform" in load_type_homo:
            val_load_homo = st.number_input("น้ำหนักแผ่กระจาย w (kg/m)", min_value=1.0, value=500.0, step=50.0, key="w_homo")
        else:
            val_load_homo = st.number_input("น้ำหนักกระทำจุดกึ่งกลาง P (kg)", min_value=1.0, value=2000.0, step=100.0, key="P_homo")
            
    with col2:
        material_dict = {
            "เหล็กรูปพรรณ (SS400)": 1200.0,
            "ไม้เนื้อแข็งมาก (เช่น ไม้เต็ง, ไม้แดง)": 120.0,
            "ไม้เนื้อแข็งปานกลาง (เช่น ไม้ตะแบก)": 90.0,
            "ไม้เนื้ออ่อน (เช่น ไม้ยาง)": 60.0,
            "กำหนดค่าเอง (Custom)": 0.0
        }
        selected_mat = st.selectbox("เลือกประเภทวัสดุ", list(material_dict.keys()), key="mat_homo")
        
        if selected_mat == "กำหนดค่าเอง (Custom)":
            sigma_allow = st.number_input("ระบุหน่วยแรงดัดที่ยอมให้ (kg/cm²)", min_value=1.0, value=100.0, key="sig_homo")
        else:
            sigma_allow = material_dict[selected_mat]
            st.info(f"หน่วยแรงดัดที่ยอมให้ = **{sigma_allow}** kg/cm²")
            
        ratio = st.number_input("สัดส่วน ความลึก ต่อ ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5, key="ratio_homo")

    if st.button("🚀 คำนวณหน้าตัดเหล็ก/ไม้", type="primary", key="btn_homo"):
        # คำนวณโมเมนต์ตามประเภทน้ำหนัก
        if "Uniform" in load_type_homo:
            M_max = (val_load_homo * L_homo**2) / 8
        else:
            M_max = (val_load_homo * L_homo) / 4
            
        M_max_cm = M_max * 100
        S_req = M_max_cm / sigma_allow
        
        b_exact = math.pow((6 * S_req) / (ratio**2), 1/3)
        h_exact = ratio * b_exact
        b_rounded, h_rounded = math.ceil(b_exact), math.ceil(h_exact)
        
        st.divider()
        st.header("📊 2. สรุปผลการออกแบบ")
        c1, c2 = st.columns(2)
        c1.metric("โมเมนต์ดัดสูงสุด (M_max)", f"{M_max:,.2f} kg-m")
        c2.metric("Section Modulus ที่ต้องการ", f"{S_req:,.2f} cm³")
        st.success(f"### 📐 ขนาดหน้าตัดแนะนำ: กว้าง {b_rounded} ซม. × ลึก {h_rounded} ซม.")
        
        st.divider()
        st.header("📖 3. วิธีการคำนวณ (Step-by-Step)")
        
        if "Uniform" in load_type_homo:
            st.latex(r"M_{max} = \frac{w \cdot L^2}{8}")
            st.latex(rf"M_{{max}} = \frac{{{val_load_homo} \cdot {L_homo}^2}}{{8}} = {M_max:,.2f} \text{{ kg-m}}")
        else:
            st.latex(r"M_{max} = \frac{P \cdot L}{4}")
            st.latex(rf"M_{{max}} = \frac{{{val_load_homo} \cdot {L_homo}}}{{4}} = {M_max:,.2f} \text{{ kg-m}}")
            
        st.latex(rf"\rightarrow {M_max_cm:,.2f} \text{{ kg-cm}}")
        st.latex(r"S_{req} = \frac{M_{max}}{\sigma_{allow}}")
        st.latex(rf"S_{{req}} = \frac{{{M_max_cm:,.2f}}}{{{sigma_allow}}} = {S_req:,.2f} \text{{ cm}}^3")
        st.latex(r"b = \sqrt[3]{\frac{S_{req} \cdot 6}{(h/b)^2}}")
        st.latex(rf"b = \sqrt[3]{{\frac{{{S_req:,.2f} \cdot 6}}{{{ratio}^2}}}} = {b_exact:.2f} \text{{ cm}} \rightarrow \text{{ปัดเศษเป็น }} {b_rounded} \text{{ cm}}")
        st.latex(rf"h = {ratio} \cdot {b_exact:.2f} = {h_exact:.2f} \text{{ cm}} \rightarrow \text{{ปัดเศษเป็น }} {h_rounded} \text{{ cm}}")

# ==========================================
# TAB 2: คอนกรีตเสริมเหล็ก (RC Beam)
# ==========================================
with tab2:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (คาน RC)")
    
    col3, col4 = st.columns(2)
    with col3:
        L_rc = st.number_input("ความยาวช่วงคาน L (เมตร)", min_value=0.1, value=4.0, step=0.5, key="L_rc")
        
        # เลือกประเภทน้ำหนักบรรทุก
        load_type_rc = st.radio("รูปแบบน้ำหนักบรรทุก", ["น้ำหนักแผ่กระจาย (Uniform Load)", "น้ำหนักกระทำเป็นจุดกึ่งกลาง (Point Load)"], key="load_rc")
        if "Uniform" in load_type_rc:
            val_load_rc = st.number_input("น้ำหนักแผ่กระจายรวม w (kg/m)", min_value=1.0, value=1500.0, step=100.0, key="w_rc")
        else:
            val_load_rc = st.number_input("น้ำหนักกระทำจุดกึ่งกลาง P (kg)", min_value=1.0, value=6000.0, step=100.0, key="P_rc")
    
    with col4:
        steel_dict = {
            "เหล็กข้ออ้อย SD30 (fs = 1,200 kg/cm²)": 1200.0,
            "เหล็กข้ออ้อย SD40 (fs = 1,500 kg/cm²)": 1500.0
        }
        selected_steel = st.selectbox("เลือกชั้นคุณภาพเหล็กเสริมหลัก (Main Rebar)", list(steel_dict.keys()), key="steel_rc")
        fs = steel_dict[selected_steel]
        
        j_val = st.number_input("สัมประสิทธิ์แขนโมเมนต์ (j)", min_value=0.8, max_value=0.9, value=0.875, step=0.005, help="แนะนำ 0.875 สำหรับ WSD")

    if st.button("🚀 ประเมินขนาดคานและเหล็กเสริม", type="primary", key="btn_rc"):
        # คำนวณโมเมนต์ตามประเภทน้ำหนัก
        if "Uniform" in load_type_rc:
            M_rc = (val_load_rc * L_rc**2) / 8
        else:
            M_rc = (val_load_rc * L_rc) / 4
            
        M_rc_cm = M_rc * 100
        
        h_est_raw = (L_rc * 100) / 10
        h_rc = math.ceil(h_est_raw / 5.0) * 5 
        b_est_raw = h_rc / 2
        b_rc = math.ceil(b_est_raw / 5.0) * 5 
        
        d_rc = h_rc - 5
        As_req = M_rc_cm / (fs * j_val * d_rc)
        
        n_DB12 = math.ceil(As_req / 1.13)
        n_DB16 = math.ceil(As_req / 2.01)
        n_DB20 = math.ceil(As_req / 3.14)
        
        st.divider()
        st.header("📊 2. สรุปผลการประเมินคาน RC")
        c3, c4, c5 = st.columns(3)
        c3.metric("โมเมนต์ดัดสูงสุด (M_max)", f"{M_rc:,.2f} kg-m")
        c4.metric("ขนาดหน้าตัดคานแนะนำ (b × h)", f"{b_rc} × {h_rc} ซม.")
        c5.metric("พื้นที่เหล็กเสริมรับแรงดึง (As)", f"{As_req:,.2f} cm²")
        
        st.success(f"### 🛠️ ปริมาณเหล็กเสริมที่แนะนำ (เลือกใช้อย่างใดอย่างหนึ่ง):")
        st.markdown(f"- ใช้เหล็ก **DB12** จำนวน **{n_DB12}** เส้น (พื้นที่ = {n_DB12 * 1.13:.2f} cm²)")
        st.markdown(f"- ใช้เหล็ก **DB16** จำนวน **{n_DB16}** เส้น (พื้นที่ = {n_DB16 * 2.01:.2f} cm²)")
        st.markdown(f"- ใช้เหล็ก **DB20** จำนวน **{n_DB20}** เส้น (พื้นที่ = {n_DB20 * 3.14:.2f} cm²)")
        
        st.divider()
        st.header("📖 3. วิธีการคำนวณ WSD (Step-by-Step)")
        
        st.subheader("ขั้นที่ 1: หาโมเมนต์ดัดสูงสุด")
        if "Uniform" in load_type_rc:
            st.latex(r"M_{max} = \frac{w \cdot L^2}{8}")
            st.latex(rf"M_{{max}} = \frac{{{val_load_rc} \cdot {L_rc}^2}}{{8}} = {M_rc:,.2f} \text{{ kg-m}}")
        else:
            st.latex(r"M_{max} = \frac{P \cdot L}{4}")
            st.latex(rf"M_{{max}} = \frac{{{val_load_rc} \cdot {L_rc}}}{{4}} = {M_rc:,.2f} \text{{ kg-m}}")
            
        st.latex(rf"\rightarrow {M_rc_cm:,.2f} \text{{ kg-cm}}")
        
        st.subheader("ขั้นที่ 2: ประมาณการขนาดหน้าตัด (Rule of Thumb)")
        st.latex(rf"h \approx \frac{{{L_rc} \times 100}}{{10}} = {h_est_raw:.2f} \text{{ cm}} \rightarrow \text{{เลือกใช้ }} {h_rc} \text{{ cm}}")
        st.latex(rf"b \approx \frac{{{h_rc}}}{{2}} = {b_est_raw:.2f} \text{{ cm}} \rightarrow \text{{เลือกใช้ }} {b_rc} \text{{ cm}}")
        st.latex(rf"d = h - 5 = {h_rc} - 5 = {d_rc} \text{{ cm}}")
        
        st.subheader("ขั้นที่ 3: หาพื้นที่หน้าตัดเหล็กเสริมรับแรงดึง ($A_s$)")
        st.latex(r"A_s = \frac{M_{max}}{f_s \cdot j \cdot d}")
        st.latex(rf"A_s = \frac{{{M_rc_cm:,.2f}}}{{{fs} \cdot {j_val} \cdot {d_rc}}} = {As_req:,.2f} \text{{ cm}}^2")
