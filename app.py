import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Beam Design Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น (Pro Version)")
st.markdown("ระบบวิเคราะห์หน้าตัดคานที่คำนึงถึงน้ำหนักตัวเอง (Self-weight) พร้อมการคำนวณออกแบบเหล็กเสริมและรายการคำนวณละเอียด")
st.divider()

def plot_diagrams(L, w_total, P, is_uniform):
    x = np.linspace(0, L, 500)
    if is_uniform:
        V = w_total * (L/2 - x)
        M = (w_total * x / 2) * (L - x)
    else:
        V_P = np.where(x < L/2, P/2, -P/2)
        V_w = w_total * (L/2 - x)
        V = V_P + V_w
        M_P = (P/2) * np.minimum(x, L-x)
        M_w = (w_total * x / 2) * (L - x)
        M = M_P + M_w

    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=x, y=V, fill='tozeroy', mode='lines', name='Shear Force (kg)', line=dict(color='blue')))
    fig_v.update_layout(title="Shear Force Diagram (SFD)", xaxis_title="ระยะคาน L (m)", yaxis_title="Shear Force (kg)", height=300, margin=dict(l=0, r=0, t=30, b=0))
    
    fig_m = go.Figure()
    fig_m.add_trace(go.Scatter(x=x, y=M, fill='tozeroy', mode='lines', name='Bending Moment (kg-m)', line=dict(color='red')))
    fig_m.update_layout(title="Bending Moment Diagram (BMD)", xaxis_title="ระยะคาน L (m)", yaxis_title="Moment (kg-m)", height=300, margin=dict(l=0, r=0, t=30, b=0))
    
    return fig_v, fig_m

tab1, tab2 = st.tabs(["🪵 เหล็กรูปพรรณ / ไม้ (Homogeneous)", "🧱 คอนกรีตเสริมเหล็ก (RC Beam)"])

# ==========================================
# TAB 1: เหล็กรูปพรรณ และ ไม้
# ==========================================
with tab1:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (เหล็ก/ไม้)")
    
    # เพิ่มโหมดการออกแบบ
    design_mode_homo = st.radio("โหมดการออกแบบ (เหล็ก/ไม้)", ["🔍 คำนวณขนาดอัตโนมัติ (Auto-sizing)", "✍️ กำหนดขนาดเอง (Manual)"], horizontal=True, key="mode_homo")
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        L_homo = st.number_input("ความยาวช่วงคาน L (เมตร)", min_value=0.1, value=4.0, step=0.5, key="L_homo")
        load_type_homo = st.radio("รูปแบบน้ำหนักบรรทุกภายนอก", ["น้ำหนักแผ่กระจาย (Uniform Load)", "น้ำหนักกระทำเป็นจุด (Point Load)"], key="load_homo")
        is_uniform_homo = "Uniform" in load_type_homo
        if is_uniform_homo:
            val_load_homo = st.number_input("น้ำหนักแผ่กระจาย w (kg/m)", min_value=1.0, value=500.0, step=50.0, key="w_homo")
            P_homo = 0.0
        else:
            val_load_homo = 0.0
            P_homo = st.number_input("น้ำหนักกระทำจุดกึ่งกลาง P (kg)", min_value=1.0, value=2000.0, step=100.0, key="P_homo")
            
    with c2:
        mat_db = {
            "เหล็กรูปพรรณ SS400 (โครงสร้างทั่วไป/ยึดด้วยน็อต)": [1440.0, 7850.0, 2.0e6],
            "เหล็กรูปพรรณ SM400 (งานเชื่อมโครงสร้าง/ไวด์แฟลงก์)": [1440.0, 7850.0, 2.0e6],
            "เหล็กรูปพรรณกำลังสูง SM490 (งานรับน้ำหนักมาก)": [1980.0, 7850.0, 2.0e6],
            "ไม้เนื้อแข็ง (เช่น ไม้เต็ง, ไม้แดง)": [120.0, 800.0, 1.0e5],
            "ไม้เนื้ออ่อน (เช่น ไม้ยาง)": [60.0, 600.0, 1.0e5]
        }
        selected_mat = st.selectbox("เลือกประเภทวัสดุ", list(mat_db.keys()), key="mat_homo")
        sigma_allow, density, E_val = mat_db[selected_mat]
        
        section_shape = st.selectbox("รูปแบบรูปทรงหน้าตัด", ["หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)", "หน้าตัดไวด์แฟลงก์ / เอชบีม (Wide Flange / H-Beam)"], key="shape_homo")
        
        if "Auto" in design_mode_homo:
            ratio = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5, key="ratio_homo")
            b_manual_homo, h_manual_homo = 0, 0
        else:
            col_b, col_h = st.columns(2)
            b_manual_homo = col_b.number_input("ความกว้าง b (cm)", min_value=1.0, value=15.0, step=1.0, key="b_manual_homo")
            h_manual_homo = col_h.number_input("ความลึก h (cm)", min_value=1.0, value=30.0, step=1.0, key="h_manual_homo")
            ratio = h_manual_homo / b_manual_homo if b_manual_homo > 0 else 2.0

        st.info(f"หน่วยแรงดัด (Fb): **{sigma_allow:,.0f} kg/cm²**\n\nความหนาแน่น: **{density:,.0f} kg/m³** | ค่า E: **{E_val:,.0f} kg/cm²**")
    
    if st.button("🚀 ประเมินขนาดและวิเคราะห์คาน", type="primary", key="btn_homo"):
        L_cm = L_homo * 100
        delta_allow = L_cm / 360
        M_applied = (val_load_homo * L_homo**2)/8 if is_uniform_homo else (P_homo * L_homo)/4
        
        auto_resized = False
        is_safe = True
        
        if "Auto" in design_mode_homo:
            max_iter = 1000
            iter_count = 0
            h_final = 10.0  
            
            while iter_count < max_iter:
                iter_count += 1
                b_final = math.ceil(h_final / ratio)
                
                if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)":
                    w_self_actual = (b_final / 100) * (h_final / 100) * density
                    I_prov = (b_final * h_final**3) / 12
                    S_prov = (b_final * h_final**2) / 6
                else:
                    tf = 0.06 * h_final
                    tw = 0.04 * h_final
                    area_cm2 = (2 * b_final * tf) + ((h_final - 2 * tf) * tw)
                    w_self_actual = (area_cm2 / 10000) * density
                    I_prov = (b_final * h_final**3 / 12) - ((b_final - tw) * (h_final - 2 * tf)**3 / 12)
                    S_prov = I_prov / (h_final / 2)
                    
                w_total_actual = val_load_homo + w_self_actual if is_uniform_homo else w_self_actual
                M_self = (w_self_actual * L_homo**2) / 8
                M_total = M_applied + M_self
                
                S_req_iter = (M_total * 100) / sigma_allow
                if is_uniform_homo:
                    I_req_iter = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * delta_allow)
                else:
                    I_req_iter = ((P_homo * L_cm**3) / (48 * E_val * delta_allow)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * delta_allow))
                    
                if S_prov >= S_req_iter and I_prov >= I_req_iter:
                    S_req_final = S_req_iter
                    I_req_final = I_req_iter
                    if is_uniform_homo:
                        delta_max = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * I_prov)
                    else:
                        delta_max = ((P_homo * L_cm**3) / (48 * E_val * I_prov)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * I_prov))
                    break
                else:
                    auto_resized = True
                    h_final += 1.0
            
            if iter_count >= max_iter:
                st.error("⚠️ ไม่สามารถคำนวณหน้าตัดได้ กรุณาตรวจสอบน้ำหนักบรรทุก")
                is_safe = False
                
        else:
            # โหมดกำหนดเอง (Manual)
            b_final = b_manual_homo
            h_final = h_manual_homo
            
            if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)":
                w_self_actual = (b_final / 100) * (h_final / 100) * density
                I_prov = (b_final * h_final**3) / 12
                S_prov = (b_final * h_final**2) / 6
            else:
                tf = 0.06 * h_final
                tw = 0.04 * h_final
                area_cm2 = (2 * b_final * tf) + ((h_final - 2 * tf) * tw)
                w_self_actual = (area_cm2 / 10000) * density
                I_prov = (b_final * h_final**3 / 12) - ((b_final - tw) * (h_final - 2 * tf)**3 / 12)
                S_prov = I_prov / (h_final / 2)
                
            w_total_actual = val_load_homo + w_self_actual if is_uniform_homo else w_self_actual
            M_self = (w_self_actual * L_homo**2) / 8
            M_total = M_applied + M_self
            
            S_req_final = (M_total * 100) / sigma_allow
            if is_uniform_homo:
                I_req_final = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * delta_allow)
                delta_max = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * I_prov)
            else:
                I_req_final = ((P_homo * L_cm**3) / (48 * E_val * delta_allow)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * delta_allow))
                delta_max = ((P_homo * L_cm**3) / (48 * E_val * I_prov)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * I_prov))
                
            if S_prov < S_req_final or I_prov < I_req_final:
                is_safe = False
                
        # ส่วนแสดงผลลัพธ์
        b_min_bend_final = math.pow((6 * S_req_final) / (ratio**2), 1/3) if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)" else b_final
        b_min_def_final = math.pow((12 * I_req_final) / (ratio**3), 0.25) if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)" else b_final
        b_req_theoretical = max(b_min_bend_final, b_min_def_final)
        h_req_theoretical = b_req_theoretical * ratio

        st.divider()
        st.header("📊 2. สรุปผลการประเมินหน้าตัดขั้นสุดท้าย")
        
        if not is_safe and "Manual" in design_mode_homo:
            st.error(f"❌ **ขนาดที่กำหนดไม่ปลอดภัย!** หน้าตัด {b_final}x{h_final} ซม. ไม่เพียงพอต่อการรับน้ำหนักหรือการแอ่นตัว กรุณาเพิ่มขนาด")
        elif is_safe:
            if auto_resized:
                st.warning(f"🔄 **ระบบทำการเพิ่มขนาดเผื่อน้ำหนักตัวเอง:** คานต้องรับภาระน้ำหนักตัวเองเพิ่ม {w_self_actual:,.2f} kg/m จึงได้ปรับขนาดให้ปลอดภัยขึ้น")
            st.success(f"### 📐 ขนาดที่ใช้ ({section_shape}): กว้าง {b_final:.0f} ซม. × ลึก {h_final:.0f} ซม.")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total:,.2f} kg-m")
        col_r2.metric("น้ำหนักของตัวคานเอง", f"{w_self_actual:,.2f} kg/m")
        col_r3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max:,.3f} cm", delta=f"ยอมให้ {delta_allow:,.3f} cm", delta_color="normal" if delta_max <= delta_allow else "inverse")
            
        st.divider()
        st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
        fig_v, fig_m = plot_diagrams(L_homo, w_total_actual, P_homo, is_uniform_homo)
        cp1, cp2 = st.columns(2)
        cp1.plotly_chart(fig_v, use_container_width=True)
        cp2.plotly_chart(fig_m, use_container_width=True)

        with st.expander("📝 ดูรายการคำนวณแบบละเอียด: ทฤษฎี, การหาค่าขั้นต่ำ และการเลือกขนาด"):
            st.markdown(r"### 📌 ขั้นตอนที่ 1: การหาค่าความต้องการของหน้าตัด (Required Section Properties)")
            st.markdown(r"ในการออกแบบคาน หน้าตัดจะต้องมีขนาดใหญ่พอที่จะต้านทาน **โมเมนต์ดัด (Bending Moment)** ไม่ให้วัสดุเกิดความเค้นเกินขีดจำกัด และต้องมีสติฟเนส (Stiffness) มากพอที่จะต้านทาน **การแอ่นตัว (Deflection)** ไม่ให้เกินค่าที่มาตรฐานกำหนด")
            
            st.markdown(rf"- **น้ำหนักรวมที่กระทำบนคาน ($w_{{total}}$):** {w_total_actual:,.2f} kg/m")
            st.markdown(rf"- **โมเมนต์ดัดสูงสุดที่เกิดขึ้น ($M_{{max}}$):** {M_total:,.2f} kg-m")
            
            st.markdown("---")
            st.markdown(r"**1.1 ความต้องการเพื่อต้านทานการดัด (Bending Criteria):**")
            st.latex(rf"S_{{req}} = \frac{{M_{{max}} \cdot 100}}{{\sigma_{{allow}}}} = \frac{{{M_total:,.2f} \cdot 100}}{{{sigma_allow:,.0f}}} = {S_req_final:,.2f} \text{{ cm}}^3")
            
            st.markdown(r"**1.2 ความต้องการเพื่อควบคุมการแอ่นตัว (Deflection Criteria):**")
            st.latex(rf"\Delta_{{allow}} = \frac{{L}}{{360}} = \frac{{{L_homo*100:,.0f}}}{{360}} = {delta_allow:,.3f} \text{{ cm}}")
            if is_uniform_homo:
                st.latex(rf"I_{{req}} = \frac{{5 \cdot w_{{total}} \cdot L^4}}{{384 \cdot E \cdot \Delta_{{allow}}}} = {I_req_final:,.2f} \text{{ cm}}^4")
            else:
                st.latex(rf"I_{{req}} = \left( \frac{{P \cdot L^3}}{{48 \cdot E \cdot \Delta_{{allow}}}} \right) + \left( \frac{{5 \cdot w_{{self}} \cdot L^4}}{{384 \cdot E \cdot \Delta_{{allow}}}} \right) = {I_req_final:,.2f} \text{{ cm}}^4")

            if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)":
                st.markdown("---")
                st.markdown(r"### 📌 ขั้นตอนที่ 2: การถอดสมการหาความกว้าง (b) และความลึก (h) ขั้นต่ำสุดทางทฤษฎี")
                st.latex(rf"b \ge \sqrt[3]{{\frac{{6 \cdot S_{{req}}}}{{{ratio**2}}}}} \implies b \ge {b_min_bend_final:,.2f} \text{{ cm}}")
                st.latex(rf"b \ge \sqrt[4]{{\frac{{12 \cdot I_{{req}}}}{{{ratio**3}}}}} \implies b \ge {b_min_def_final:,.2f} \text{{ cm}}")
                st.markdown(rf"**สรุปการหาค่าตามทฤษฎี:** ต้องเลือกค่า $b$ ที่สูงกว่า $\implies b_{{min}} = {b_req_theoretical:,.2f}$ cm, $h_{{min}} = {h_req_theoretical:,.2f}$ cm")
                
            st.markdown("---")
            st.markdown(r"### 📌 ขั้นตอนที่ 3: สรุปการเลือกใช้หน้าตัดจริง (Provided Section vs Required Section)")
            st.markdown(rf"โปรแกรมพิจารณาหน้าตัด: **กว้าง $b = {b_final:.0f}$ cm** และ **ลึก $h = {h_final:.0f}$ cm**")
            
            st.markdown(r"**1. ตรวจสอบพิกัดต้านทานการดัด (Section Modulus Check):**")
            pass_S = "ปลอดภัย (OK)" if S_prov >= S_req_final else "ไม่ปลอดภัย (NG)"
            st.latex(rf"S_{{prov}} ({S_prov:,.2f} \text{{ cm}}^3) \ge S_{{req}} ({S_req_final:,.2f} \text{{ cm}}^3) \implies \text{{{pass_S}}}")
            
            st.markdown(r"**2. ตรวจสอบพิกัดควบคุมการแอ่นตัว (Moment of Inertia Check):**")
            pass_I = "ปลอดภัย (OK)" if I_prov >= I_req_final else "ไม่ปลอดภัย (NG)"
            st.latex(rf"I_{{prov}} ({I_prov:,.2f} \text{{ cm}}^4) \ge I_{{req}} ({I_req_final:,.2f} \text{{ cm}}^4) \implies \text{{{pass_I}}}")

# ==========================================
# TAB 2: คอนกรีตเสริมเหล็ก (RC Beam)
# ==========================================
with tab2:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (คาน RC)")
    
    design_mode_rc = st.radio("โหมดการออกแบบ (RC Beam)", ["🔍 คำนวณขนาดอัตโนมัติ (Auto-sizing)", "✍️ กำหนดขนาดเอง (Manual)"], horizontal=True, key="mode_rc")
    st.markdown("---")
    
    c3, c4 = st.columns(2)
    with c3:
        L_rc = st.number_input("ความยาวช่วงคาน L (เมตร)", min_value=0.1, value=4.0, step=0.5, key="L_rc")
        load_type_rc = st.radio("รูปแบบน้ำหนักบรรทุกภายนอก", ["น้ำหนักแผ่กระจาย (Uniform Load)", "น้ำหนักกระทำเป็นจุด (Point Load)"], key="load_rc")
        is_uniform_rc = "Uniform" in load_type_rc
        if is_uniform_rc:
            val_load_rc = st.number_input("น้ำหนักแผ่กระจาย w (kg/m)", min_value=1.0, value=1500.0, step=100.0, key="w_rc")
            P_rc = 0.0
        else:
            val_load_rc = 0.0
            P_rc = st.number_input("น้ำหนักกระทำจุดกึ่งกลาง P (kg)", min_value=1.0, value=6000.0, step=100.0, key="P_rc")
            
    with c4:
        steel_dict = {
            "เหล็กเส้นกลม SR24 (ผิวเรียบ)": [1200.0, 2400.0],
            "เหล็กข้ออ้อย SD30": [1500.0, 3000.0],
            "เหล็กข้ออ้อย SD40": [1700.0, 4000.0],
            "เหล็กข้ออ้อย SD50 (กำลังสูง)": [1700.0, 5000.0]
        }
        selected_steel = st.selectbox("ชั้นคุณภาพเหล็กเสริมหลัก", list(steel_dict.keys()), key="steel_rc")
        fs, fy = steel_dict[selected_steel]
        fc_prime = st.selectbox("กำลังอัดของคอนกรีต f'c ทรงกระบอก (ksc)", [180, 210, 240, 280, 320], index=1, key="fc_rc")
        
        if "Auto" in design_mode_rc:
            ratio_rc = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b) ของคาน RC", min_value=1.5, value=2.0, step=0.5)
            b_manual_rc, h_manual_rc = 0, 0
        else:
            c_rc_b, c_rc_h = st.columns(2)
            b_manual_rc = c_rc_b.number_input("ความกว้างคาน b (cm)", min_value=10.0, value=20.0, step=5.0)
            h_manual_rc = c_rc_h.number_input("ความลึกคาน h (cm)", min_value=10.0, value=40.0, step=5.0)
            ratio_rc = h_manual_rc / b_manual_rc if b_manual_rc > 0 else 2.0

        fc = 0.375 * fc_prime
        Ec = 15100 * math.sqrt(fc_prime)
        Es = 2.04e6
        n_ratio = round(Es / Ec)
        k_wsd = n_ratio / (n_ratio + (fs / fc))
        j_val = 1.0 - (k_wsd / 3.0)
        R_wsd = 0.5 * fc * k_wsd * j_val
        
        st.info(f"**WSD Constants:** n = {n_ratio} | k = {k_wsd:.3f} | j = {j_val:.3f} | R = {R_wsd:.2f} ksc\n\nหน่วยแรงดึงเหล็ก (fs): **{fs:,.0f} kg/cm²**")

    if st.button("🚀 ประเมินหน้าตัดและเหล็กเสริม (RC)", type="primary", key="btn_rc"):
        L_cm_rc = L_rc * 100
        delta_allow_rc = L_cm_rc / 360
        auto_resized_rc = False
        is_rc_safe = True
        
        h_min_theoretical = L_cm_rc / 10.0
        b_min_theoretical = h_min_theoretical / ratio_rc
        
        if "Auto" in design_mode_rc:
            max_iter_rc = 1000
            iter_rc_count = 0
            h_rc = math.ceil(h_min_theoretical / 5.0) * 5
            
            while iter_rc_count < max_iter_rc:
                iter_rc_count += 1
                b_rc = math.ceil((h_rc / ratio_rc) / 5.0) * 5
                if b_rc < 15: b_rc = 15.0 
                
                w_self_rc = (b_rc / 100) * (h_rc / 100) * 2400
                
                if is_uniform_rc:
                    w_total_rc = val_load_rc + w_self_rc
                    M_total_rc = (w_total_rc * L_rc**2) / 8
                    V_max_rc = (w_total_rc * L_rc) / 2
                    I_req_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc)
                else:
                    w_total_rc = w_self_rc
                    M_total_rc = (P_rc * L_rc) / 4 + (w_self_rc * L_rc**2) / 8
                    V_max_rc = (P_rc / 2) + (w_self_rc * L_rc) / 2
                    I_req_rc = ((P_rc * L_cm_rc**3) / (48 * Ec * delta_allow_rc)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc))
                    
                I_g = (b_rc * h_rc**3) / 12
                d_rc = h_rc - 5.0 
                M_concrete_capacity = (R_wsd * b_rc * d_rc**2) / 100 
                
                if I_g >= I_req_rc and M_concrete_capacity >= M_total_rc:
                    if is_uniform_rc:
                        delta_max_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g)
                    else:
                        delta_max_rc = ((P_rc * L_cm_rc**3) / (48 * Ec * I_g)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g))
                    break
                else:
                    auto_resized_rc = True
                    h_rc += 5.0 
                    
            if iter_rc_count >= max_iter_rc:
                st.error("⚠️ ไม่สามารถประเมินหน้าตัดคาน RC ได้เนื่องจากน้ำหนักกระทำสูงเกินเกณฑ์ขีดจำกัด")
                is_rc_safe = False
                
        else:
            # โหมดกำหนดเอง (Manual RC)
            b_rc = b_manual_rc
            h_rc = h_manual_rc
            w_self_rc = (b_rc / 100) * (h_rc / 100) * 2400
            
            if is_uniform_rc:
                w_total_rc = val_load_rc + w_self_rc
                M_total_rc = (w_total_rc * L_rc**2) / 8
                V_max_rc = (w_total_rc * L_rc) / 2
                I_req_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc)
            else:
                w_total_rc = w_self_rc
                M_total_rc = (P_rc * L_rc) / 4 + (w_self_rc * L_rc**2) / 8
                V_max_rc = (P_rc / 2) + (w_self_rc * L_rc) / 2
                I_req_rc = ((P_rc * L_cm_rc**3) / (48 * Ec * delta_allow_rc)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc))
                
            I_g = (b_rc * h_rc**3) / 12
            d_rc = h_rc - 5.0 
            M_concrete_capacity = (R_wsd * b_rc * d_rc**2) / 100 
            
            if is_uniform_rc:
                delta_max_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g)
            else:
                delta_max_rc = ((P_rc * L_cm_rc**3) / (48 * Ec * I_g)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g))
                
            if I_g < I_req_rc or M_concrete_capacity < M_total_rc:
                is_rc_safe = False

        if "is_rc_safe" in locals(): # ดำเนินการต่อถ้าไม่มี Error ขีดจำกัด
            As_req = (M_total_rc * 100) / (fs * j_val * d_rc) if d_rc > 0 else 0
            As_min = (14.0 / fy) * b_rc * d_rc
            As_final = max(As_req, As_min)
            
            n_DB12 = math.ceil(As_final / 1.13)
            n_DB16 = math.ceil(As_final / 2.01)
            
            v_v = V_max_rc / (b_rc * d_rc) if b_rc*d_rc > 0 else 0
            v_c = 0.29 * math.sqrt(fc_prime) 
            stirrup_bar = "RB6" if h_rc <= 40 else "RB9"
            Av = 2 * 0.283 if stirrup_bar == "RB6" else 2 * 0.636
            fv_stirrup = 1200.0
            
            if v_v <= v_c:
                stirrup_text = f"คอนกรีตรับแรงเฉือนได้พอ แนะนำใส่เหล็กปลอกกันร้าว"
                s_spacing = min(d_rc / 2, 30.0)
            else:
                v_s = v_v - v_c
                v_max_allow = 1.32 * math.sqrt(fc_prime)
                if v_s > v_max_allow:
                    stirrup_text = "⚠️ หน้าตัดเล็กเกินไปสำหรับรับแรงเฉือนสูงสุด!"
                    s_spacing = 0
                    is_rc_safe = False
                else:
                    stirrup_text = f"ต้องเสริมเหล็กปลอกเพื่อช่วยรับแรงเฉือน"
                    s_spacing = (Av * fv_stirrup) / (v_s * b_rc)
                    s_spacing = min(s_spacing, d_rc / 2, 30.0)
            
            s_spacing_final = math.floor(s_spacing) if s_spacing > 0 else 0

            st.divider()
            st.header("📊 2. สรุปผลการประเมินคานคอนกรีตเสริมเหล็ก")
            
            if not is_rc_safe and "Manual" in design_mode_rc:
                st.error(f"❌ **ขนาดคานที่กำหนด ({b_rc}x{h_rc} ซม.) ไม่ปลอดภัย!** โมเมนต์ที่เกิดขึ้นเกินกำลังคอนกรีต ($M_c$) หรือหน้าตัดไม่ผ่านเกณฑ์การแอ่นตัว/แรงเฉือน กรุณาขยายขนาด")
            elif is_rc_safe:
                if auto_resized_rc:
                    st.warning(f"🔄 **ระบบทำการปรับเพิ่มขนาดคาน:** เพื่อให้ค่าหน้าตัดผ่านเกณฑ์โมเมนต์ความเฉื่อย ($I_{{gross}}$) และกำลังของคอนกรีต")
                st.success(f"### 📐 หน้าตัดคาน RC ที่ใช้งาน: กว้าง {b_rc:.0f} ซม. × ลึก {h_rc:.0f} ซม.")
            
            c_out1, c_out2, c_out3 = st.columns(3)
            c_out1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total_rc:,.2f} kg-m")
            c_out2.metric("พื้นที่เหล็กแกนดึง (As)", f"{As_final:,.2f} cm²", delta=f"เหล็กขั้นต่ำ {As_min:.2f} cm²")
            c_out3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max_rc:,.3f} cm", delta=f"ยอมให้ {delta_allow_rc:,.2f} cm", delta_color="normal" if delta_max_rc <= delta_allow_rc else "inverse")
            
            if is_rc_safe or "Manual" in design_mode_rc:
                st.info(f"**🛠️ ปริมาณเหล็กเสริมหลัก:** แนะนำใช้ข้ออ้อย DB12 จำนวน {max(2, n_DB12)} เส้น หรือ DB16 จำนวน {max(2, n_DB16)} เส้น")
                if s_spacing_final > 0:
                    st.warning(f"**🛡️ เหล็กปลอกรับแรงเฉือน:** {stirrup_text} ใช้ **{stirrup_bar} @ {s_spacing_final} ซม.**")
                elif not is_rc_safe and s_spacing == 0:
                    st.error(f"**🛡️ เหล็กปลอกรับแรงเฉือน:** {stirrup_text} คอนกรีตจะระเบิดจากแรงเฉือน ต้องขยายขนาดหน้าตัด")
                
            st.divider()
            st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
            fig_v_rc, fig_m_rc = plot_diagrams(L_rc, w_total_rc, P_rc, is_uniform_rc)
            cr1, cr2 = st.columns(2)
            cr1.plotly_chart(fig_v_rc, use_container_width=True)
            cr2.plotly_chart(fig_m_rc, use_container_width=True)

            with st.expander("📝 ดูรายการคำนวณ: การหาความลึกขั้นต่ำ ปริมาณเหล็ก และแรงเฉือน"):
                st.markdown("### 📌 ขั้นตอนที่ 1: หาความลึกขั้นต่ำของคอนกรีต (Minimum Required Section)")
                st.latex(rf"h_{{min}} = \frac{{L}}{{10}} = \frac{{{L_cm_rc}}}{{10}} = {h_min_theoretical:,.2f} \text{{ cm}}")
                st.markdown(rf"กำหนดสัดส่วนความกว้าง $b \approx h/{ratio_rc} \implies b_{{min}} = {b_min_theoretical:,.2f}$ cm")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 2: สรุปการเลือกหน้าตัด (Provided Section)")
                st.markdown(f"เลือกหน้าตัดใช้งานที่: **กว้าง $b = {b_rc:.0f}$ cm** และ **ลึก $h = {h_rc:.0f}$ cm**")
                
                pass_I_rc = "OK" if I_g >= I_req_rc else "NG (ไม่ผ่าน)"
                st.markdown(f"ตรวจสอบโมเมนต์ความเฉื่อยเพื่อควบคุมการแอ่นตัว ($I_{{req}} = {I_req_rc:,.2f}$ cm$^4$):")
                st.latex(rf"I_{{gross}} = \frac{{{b_rc:.0f} \cdot {h_rc:.0f}^3}}{{12}} = {I_g:,.2f} \text{{ cm}}^4 \ge I_{{req}} \implies \text{{{pass_I_rc}}}")
                
                pass_Mc = "OK" if M_concrete_capacity >= M_total_rc else "NG (คอนกรีตรับไม่ไหว)"
                st.markdown(f"ตรวจสอบกำลังต้านทานโมเมนต์อัดของคอนกรีต ($M_c = Rbd^2$):")
                st.latex(rf"M_c = \frac{{{R_wsd:.2f} \cdot {b_rc:.0f} \cdot {d_rc}^2}}{{100}} = {M_concrete_capacity:,.2f} \text{{ kg-m}} \ge {M_total_rc:,.2f} \implies \text{{{pass_Mc}}}")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 3: คำนวณหาพื้นที่เหล็กเสริมรับแรงดึง (Required Main Rebar)")
                st.latex(rf"A_s = \frac{{M_{{max}} \cdot 100}}{{f_s \cdot j \cdot d}} = \frac{{{M_total_rc:,.2f} \cdot 100}}{{{fs:,.0f} \cdot {j_val:.3f} \cdot {d_rc}}} = {As_req:,.2f} \text{{ cm}}^2")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 4: การตรวจสอบและออกแบบเหล็กปลอก (Shear Design)")
                st.latex(rf"v_v = \frac{{V_{{max}}}}{{b \cdot d}} = \frac{{{V_max_rc:,.2f}}}{{{b_rc:.0f} \cdot {d_rc}}} = {v_v:.2f} \text{{ ksc}}")
                st.latex(rf"v_c = 0.29\sqrt{{f'_c}} = 0.29\sqrt{{{fc_prime}}} = {v_c:.2f} \text{{ ksc}}")
                if v_v > v_c:
                    st.latex(rf"v_s = v_v - v_c = {v_v:.2f} - {v_c:.2f} = {v_s:.2f} \text{{ ksc}}")
                    if s_spacing > 0:
                        st.latex(rf"S = \frac{{A_v \cdot f_v}}{{v_s \cdot b}} = \frac{{{Av:.3f} \cdot {fv_stirrup:,.0f}}}{{{v_s:.2f} \cdot {b_rc:.0f}}} = {s_spacing:.2f} \text{{ cm}} \implies \text{{ใช้ }} {s_spacing_final} \text{{ cm}}")
