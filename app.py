import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Beam Design Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น (Pro Version)")
st.markdown("ระบบวิเคราะห์หน้าตัดคานที่คำนึงถึงน้ำหนักตัวเอง (Self-weight iteration) พร้อมรายการคำนวณหาค่าขั้นต่ำแบบละเอียด")
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
        # ฐานข้อมูลวัสดุ: [Allowable Bending Stress Fb (kg/cm²), Density (kg/m³), E (kg/cm²)]
        # อ้างอิงตามทฤษฎี WSD: Fb = 0.6 * Fy
        mat_db = {
            "เหล็กรูปพรรณ SS400 (โครงสร้างทั่วไป/ยึดด้วยน็อต)": [1440.0, 7850.0, 2.0e6],       # Fy ~2,400 ksc
            "เหล็กรูปพรรณ SM400 (งานเชื่อมโครงสร้าง/ไวด์แฟลงก์)": [1440.0, 7850.0, 2.0e6],    # Fy ~2,400 ksc (เชื่อมดีกว่า SS)
            "เหล็กรูปพรรณกำลังสูง SM490 (งานรับน้ำหนักมาก)": [1980.0, 7850.0, 2.0e6],        # Fy ~3,300 ksc
            "เหล็กรูปพรรณกำลังสูง SM520 (ตึกสูง/สแปนยาวมาก)": [2160.0, 7850.0, 2.0e6],        # Fy ~3,600 ksc
            "เหล็กมาตรฐานอเมริกา A36 (ไวด์แฟลงก์นำเข้าบางรุ่น)": [1500.0, 7850.0, 2.0e6],     # Fy ~2,500 ksc
            "เหล็กมาตรฐานอเมริกา เกรด 50 (A992/A572-50)": [2070.0, 7850.0, 2.0e6],        # Fy ~3,450 ksc
            "เหล็กรีดเย็นตัวซี/กล่อง (Cold-formed มอก.)": [1440.0, 7850.0, 2.0e6],         # สำหรับคานหลังคา/งานเบา
            "อลูมิเนียมอัลลอย (6061-T6 สำหรับงานสถาปัตย์)": [950.0, 2700.0, 0.7e6],           
            "ไม้เนื้อแข็ง (เช่น ไม้เต็ง, ไม้แดง)": [120.0, 800.0, 1.0e5],
            "ไม้เนื้ออ่อน (เช่น ไม้ยาง)": [60.0, 600.0, 1.0e5]
        }
        selected_mat = st.selectbox("เลือกประเภทวัสดุ", list(mat_db.keys()), key="mat_homo")
        sigma_allow, density, E_val = mat_db[selected_mat]
        st.info(f"หน่วยแรงดัด (Fb): **{sigma_allow:,.0f} kg/cm²**\n\nความหนาแน่น: **{density:,.0f} kg/m³** | ค่า E: **{E_val:,.0f} kg/cm²**")
        ratio = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5, key="ratio_homo")
    
    if st.button("🚀 ประเมินขนาดและวิเคราะห์คาน", type="primary", key="btn_homo"):
        L_cm = L_homo * 100
        delta_allow = L_cm / 360
        M_applied = (val_load_homo * L_homo**2)/8 if is_uniform_homo else (P_homo * L_homo)/4
        
        # 1. การประเมินขนาดเบื้องต้น (Initial Guess)
        S_req_initial = (M_applied * 100) / sigma_allow
        if is_uniform_homo:
            I_req_initial = (5 * (val_load_homo / 100) * L_cm**4) / (384 * E_val * delta_allow)
        else:
            I_req_initial = (P_homo * L_cm**3) / (48 * E_val * delta_allow)

        b_init = max(math.pow((6 * S_req_initial) / (ratio**2), 1/3), math.pow((12 * I_req_initial) / (ratio**3), 0.25))
        b_final = math.ceil(b_init)
        h_final = math.ceil(ratio * b_final)
        
        auto_resized = False
        max_iter = 1000
        iter_count = 0
        
        # 2. กระบวนการวนลูปเพื่อครอบคลุมน้ำหนักคานตัวเอง (Iteration for Self-weight)
        while iter_count < max_iter:
            iter_count += 1
            w_self_actual = (b_final / 100) * (h_final / 100) * density
            w_total_actual = val_load_homo + w_self_actual
            
            M_self = (w_self_actual * L_homo**2) / 8
            M_total = M_applied + M_self
            
            # คำนวณค่าที่ต้องการ (Required) ในรอบนี้
            S_req_iter = (M_total * 100) / sigma_allow
            if is_uniform_homo:
                I_req_iter = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * delta_allow)
            else:
                I_req_iter = ((P_homo * L_cm**3) / (48 * E_val * delta_allow)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * delta_allow))
                
            # คำนวณค่าที่จัดให้ (Provided)
            S_prov = (b_final * h_final**2) / 6
            I_prov = (b_final * h_final**3) / 12
            
            # ตรวจสอบความปลอดภัยทั้ง 2 ด้าน (Bending & Deflection)
            if S_prov >= S_req_iter and I_prov >= I_req_iter:
                # บันทึกค่าพารามิเตอร์สูงสุดของระบบเพื่อนำไปใช้ในรายการคำนวณ
                S_req_final = S_req_iter
                I_req_final = I_req_iter
                
                if is_uniform_homo:
                    delta_max = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * I_prov)
                else:
                    delta_max = ((P_homo * L_cm**3) / (48 * E_val * I_prov)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * I_prov))
                break
            else:
                auto_resized = True
                b_final += 1
                h_final = math.ceil(b_final * ratio)
                
        if iter_count >= max_iter:
            st.error("⚠️ ไม่สามารถคำนวณหน้าตัดได้ กรุณาตรวจสอบน้ำหนักบรรทุกว่าสูงเกินไปสำหรับวัสดุนี้หรือไม่")
        else:
            # คำนวณหา b ขั้นต่ำทางทฤษฎีจากโหลดรวมสุดท้าย (เพื่อแสดงใน Report)
            b_min_bend_final = math.pow((6 * S_req_final) / (ratio**2), 1/3)
            b_min_def_final = math.pow((12 * I_req_final) / (ratio**3), 0.25)
            b_req_theoretical = max(b_min_bend_final, b_min_def_final)
            h_req_theoretical = b_req_theoretical * ratio

            st.divider()
            st.header("📊 2. สรุปผลการประเมินหน้าตัดขั้นสุดท้าย")
            
            if auto_resized:
                st.warning(f"🔄 **ระบบทำการเพิ่มขนาดเผื่อน้ำหนักตัวเอง:** คานต้องรับภาระน้ำหนักตัวเองเพิ่ม {w_self_actual:,.2f} kg/m จึงได้ปรับขนาดให้ปลอดภัยขึ้น")
                
            st.success(f"### 📐 ขนาดหน้าตัดที่แนะนำ: กว้าง {b_final} ซม. × ลึก {h_final} ซม.")
            
            col_r1, col_r2, col_r3 = st.columns(3)
            col_r1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total:,.2f} kg-m")
            col_r2.metric("น้ำหนักของตัวคานเอง", f"{w_self_actual:,.2f} kg/m")
            col_r3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max:,.3f} cm", delta=f"ยอมให้ {delta_allow:,.3f} cm", delta_color="normal")
                
            st.divider()
            st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
            fig_v, fig_m = plot_diagrams(L_homo, w_total_actual, P_homo, is_uniform_homo)
            cp1, cp2 = st.columns(2)
            cp1.plotly_chart(fig_v, use_container_width=True)
            cp2.plotly_chart(fig_m, use_container_width=True)

            # ================= รายการคำนวณ (Tab 1) =================
            with st.expander("📝 ดูรายการคำนวณ: การหาค่าขั้นต่ำและการเลือกขนาด (Minimum Required & Provided Section)"):
                st.markdown("### 📌 ขั้นตอนที่ 1: การหาค่าความต้องการของหน้าตัดจากน้ำหนักทั้งหมด (Required Properties)")
                st.markdown(f"เมื่อพิจารณารวมน้ำหนักคานประเมินแล้ว ($w_{{total}} = {w_total_actual:,.2f}$ kg/m) โมเมนต์สูงสุดคือ $M_{{max}} = {M_total:,.2f}$ kg-m")
                
                st.markdown("**1. ความต้องการเพื่อต้านทานการดัด (Bending):**")
                st.latex(rf"S_{{req}} = \frac{{M_{{max}} \cdot 100}}{{\sigma_{{allow}}}} = \frac{{{M_total:,.2f} \cdot 100}}{{{sigma_allow:,.0f}}} = {S_req_final:,.2f} \text{{ cm}}^3")
                
                st.markdown("**2. ความต้องการเพื่อควบคุมการแอ่นตัว (Deflection):**")
                st.latex(rf"\Delta_{{allow}} = \frac{{L}}{{360}} = {delta_allow:,.3f} \text{{ cm}}")
                if is_uniform_homo:
                    st.latex(rf"I_{{req}} = \frac{{5 \cdot w_{{total}} \cdot L^4}}{{384 \cdot E \cdot \Delta_{{allow}}}} = {I_req_final:,.2f} \text{{ cm}}^4")
                else:
                    st.latex(rf"I_{{req}} = \frac{{P \cdot L^3}}{{48 \cdot E \cdot \Delta_{{allow}}}} + \frac{{5 \cdot w_{{self}} \cdot L^4}}{{384 \cdot E \cdot \Delta_{{allow}}}} = {I_req_final:,.2f} \text{{ cm}}^4")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 2: การถอดสมการหาความกว้าง (b) และความลึก (h) ขั้นต่ำสุดทางทฤษฎี")
                st.markdown(f"จากสัดส่วนที่ระบุคือ $h = {ratio}b$ เราสามารถย้อนหาค่า $b$ ขั้นต่ำได้ดังนี้:")
                
                st.markdown("**1. ขนาดหน้าตัดขั้นต่ำจากเกณฑ์โมเมนต์ดัด:**")
                st.latex(rf"S = \frac{{b \cdot ({ratio}b)^2}}{{6}} \implies b \ge \sqrt[3]{{\frac{{6 \cdot S_{{req}}}}{{{ratio**2}}}}} \implies b \ge {b_min_bend_final:,.2f} \text{{ cm}}")

                st.markdown("**2. ขนาดหน้าตัดขั้นต่ำจากเกณฑ์การแอ่นตัว:**")
                st.latex(rf"I = \frac{{b \cdot ({ratio}b)^3}}{{12}} \implies b \ge \sqrt[4]{{\frac{{12 \cdot I_{{req}}}}{{{ratio**3}}}}} \implies b \ge {b_min_def_final:,.2f} \text{{ cm}}")

                st.markdown(f"**สรุป:** เลือกค่า $b$ ที่มากกว่า $\\implies b_{{min}} = {b_req_theoretical:,.2f}$ cm")
                st.markdown(f"จะได้ $h_{{min}} = {ratio} \times {b_req_theoretical:,.2f} = {h_req_theoretical:,.2f}$ cm")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 3: สรุปการเลือกใช้หน้าตัดจริง (Provided Section)")
                st.markdown(f"ปัดเศษเพื่อให้ได้ขนาดมาตรฐาน เลือกใช้: **กว้าง $b = {b_final}$ cm** และ **ลึก $h = {h_final}$ cm**")
                st.latex(rf"S_{{prov}} = \frac{{{b_final} \cdot {h_final}^2}}{{6}} = {S_prov:,.2f} \text{{ cm}}^3 \ge {S_req_final:,.2f} \text{{ (OK)}}")
                st.latex(rf"I_{{prov}} = \frac{{{b_final} \cdot {h_final}^3}}{{12}} = {I_prov:,.2f} \text{{ cm}}^4 \ge {I_req_final:,.2f} \text{{ (OK)}}")

# ==========================================
# TAB 2: คอนกรีตเสริมเหล็ก (RC Beam)
# ==========================================
with tab2:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (คาน RC)")
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
        # ฐานข้อมูลเหล็กเสริมตามมาตรฐาน วสท. (วิธี WSD)
        # ค่าใน Dict คือ Allowable Tensile Stress (fs) ในหน่วย kg/cm²
        steel_dict = {
            "เหล็กเส้นกลม SR24 (ผิวเรียบ)": 1200.0,
            "เหล็กข้ออ้อย SD30": 1500.0,
            "เหล็กข้ออ้อย SD40": 1700.0,
            "เหล็กข้ออ้อย SD50 (กำลังสูง)": 1700.0
        }
        selected_steel = st.selectbox("ชั้นคุณภาพเหล็กเสริมหลัก", list(steel_dict.keys()), key="steel_rc")
        fs = steel_dict[selected_steel]
        
        # ค่า j ประมาณ 0.875 สำหรับการประเมินเบื้องต้น
        j_val = 0.875 
        
        st.info(f"หน่วยแรงดึงเหล็ก (fs): **{fs:,.0f} kg/cm²**\n\nความหนาแน่นคอนกรีต: **2,400 kg/m³** | โมดูลัส (E): **~200,000 kg/cm²**")

    if st.button("🚀 ประเมินหน้าตัดและเหล็กเสริม (RC)", type="primary", key="btn_rc"):
        
        L_cm_rc = L_rc * 100
        # ตามมาตรฐาน (เช่น ACI) คานช่วงเดียวสามารถอ้างอิงความลึกขั้นต่ำที่ L/16 ถึง L/10 
        # ในที่นี้ใช้ L/10 เพื่อให้หน้าตัดมีความแข็งเกร็งเพียงพอโดยไม่ต้องวิเคราะห์ Deflection เชิงลึก
        h_min_theoretical = L_cm_rc / 10.0
        b_min_theoretical = h_min_theoretical / 2.0
        
        h_rc = math.ceil(h_min_theoretical / 5.0) * 5
        b_rc = math.ceil((h_rc / 2) / 5.0) * 5
        
        delta_allow_rc = L_cm_rc / 360
        E_c = 2.0e5
        auto_resized_rc = False
        max_iter_rc = 1000
        iter_rc_count = 0
        
        # วนลูปตรวจสอบ Deflection ร่วมกับการเพิ่มน้ำหนักหน้าตัด
        while iter_rc_count < max_iter_rc:
            iter_rc_count += 1
            w_self_rc = (b_rc / 100) * (h_rc / 100) * 2400
            w_total_rc = val_load_rc + w_self_rc
            I_g = (b_rc * h_rc**3) / 12
            
            # ตรวจสอบโมเมนต์ความเฉื่อยที่ต้องการ (I_req) ณ โหลดปัจจุบัน
            if is_uniform_rc:
                I_req_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * E_c * delta_allow_rc)
            else:
                I_req_rc = ((P_rc * L_cm_rc**3) / (48 * E_c * delta_allow_rc)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * E_c * delta_allow_rc))
            
            if I_g >= I_req_rc:
                if is_uniform_rc:
                    delta_max_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * E_c * I_g)
                else:
                    delta_max_rc = ((P_rc * L_cm_rc**3) / (48 * E_c * I_g)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * E_c * I_g))
                break
            else:
                auto_resized_rc = True
                h_rc += 5
                b_rc = math.ceil((h_rc / 2) / 5.0) * 5
                
        if iter_rc_count >= max_iter_rc:
             st.error("⚠️ ไม่สามารถคำนวณหน้าตัดได้ กรุณาตรวจสอบน้ำหนักบรรทุก")
        else:
            M_applied_rc = (val_load_rc * L_rc**2)/8 if is_uniform_rc else (P_rc * L_rc)/4
            M_self_rc = (w_self_rc * L_rc**2) / 8
            M_total_rc = M_applied_rc + M_self_rc
            
            d_rc = h_rc - 5
            As_req = (M_total_rc * 100) / (fs * j_val * d_rc)
            
            n_DB12 = math.ceil(As_req / 1.13)
            n_DB16 = math.ceil(As_req / 2.01)

            st.divider()
            st.header("📊 2. สรุปผลการประเมิน (คาน RC)")
            
            if auto_resized_rc:
                st.warning(f"🔄 **ระบบทำการปรับเพิ่มขนาดคาน:** เพื่อให้ค่าโมเมนต์ความเฉื่อย ($I_{{gross}}$) มากกว่าค่าขั้นต่ำที่ต้องการ")
                
            st.success(f"### 📐 หน้าตัดคานที่แนะนำ: กว้าง {b_rc} × ลึก {h_rc} ซม.")
            
            c_out1, c_out2, c_out3 = st.columns(3)
            c_out1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total_rc:,.2f} kg-m")
            c_out2.metric("พื้นที่เหล็กเสริมรับแรงดึง (As)", f"{As_req:,.2f} cm²")
            c_out3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max_rc:,.3f} cm", delta=f"ยอมให้ {delta_allow_rc:,.2f} cm", delta_color="normal")
            
            st.info(f"**🛠️ ปริมาณเหล็กเสริมหลัก:** แนะนำใช้ข้ออ้อย DB12 จำนวน {n_DB12} เส้น หรือ DB16 จำนวน {n_DB16} เส้น")
                
            st.divider()
            st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
            fig_v_rc, fig_m_rc = plot_diagrams(L_rc, w_total_rc, P_rc, is_uniform_rc)
            cr1, cr2 = st.columns(2)
            cr1.plotly_chart(fig_v_rc, use_container_width=True)
            cr2.plotly_chart(fig_m_rc, use_container_width=True)

            # ================= รายการคำนวณ (Tab 2) =================
            with st.expander("📝 ดูรายการคำนวณ: การหาความลึกขั้นต่ำ และปริมาณเหล็ก"):
                st.markdown("### 📌 ขั้นตอนที่ 1: หาความลึกขั้นต่ำของคอนกรีต (Minimum Required Section)")
                st.markdown("ตามข้อกำหนดทางวิศวกรรม (เช่น มาตรฐาน ACI) สำหรับคานช่วงเดียว เพื่อควบคุมไม่ให้เกิดการแอ่นตัวมากเกินไป สามารถอ้างอิงความลึกขั้นต่ำที่ $L/10$ ถึง $L/16$ (ในที่นี้ใช้ $L/10$ เพื่อความแข็งแกร่งสูงสุด):")
                st.latex(rf"h_{{min}} = \frac{{L}}{{10}} = \frac{{{L_cm_rc}}}{{10}} = {h_min_theoretical:,.2f} \text{{ cm}}")
                st.markdown(f"กำหนดสัดส่วนความกว้าง $b \approx h/2$ $\\implies b_{{min}} = {b_min_theoretical:,.2f}$ cm")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 2: สรุปการเลือกหน้าตัด (Provided Section)")
                st.markdown(f"ทำการปัดเลขให้ทำงานก่อสร้างได้จริงแบบลงตัว เลือกใช้: **กว้าง $b = {b_rc}$ cm** และ **ลึก $h = {h_rc}$ cm**")
                st.markdown(f"ตรวจสอบโมเมนต์ความเฉื่อยเพื่อควบคุมการแอ่นตัว ($I_{{req}} = {I_req_rc:,.2f}$ cm$^4$):")
                st.latex(rf"I_{{gross}} = \frac{{{b_rc} \cdot {h_rc}^3}}{{12}} = {I_g:,.2f} \text{{ cm}}^4 \ge I_{{req}} \text{{ (OK)}}")
                
                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 3: คำนวณหาพื้นที่เหล็กเสริมรับแรงดึง (Required Main Rebar)")
                st.markdown(f"จากหน้าตัดที่เลือก และโมเมนต์ดัดรวม $M_{{total}} = {M_total_rc:,.2f}$ kg-m (ใช้วิธี Working Stress Design):")
                st.latex(rf"d_{{prov}} = h - 5 = {h_rc} - 5 = {d_rc} \text{{ cm}}")
                st.latex(rf"A_s = \frac{{M_{{max}} \cdot 100}}{{f_s \cdot j \cdot d}} = \frac{{{M_total_rc:,.2f} \cdot 100}}{{{fs:,.0f} \cdot {j_val} \cdot {d_rc}}} = {As_req:,.2f} \text{{ cm}}^2")
