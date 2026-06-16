import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Beam Design Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น (Pro Version)")
st.markdown("ระบบวิเคราะห์หน้าตัดคานที่คำนึงถึงน้ำหนักตัวเอง (Self-weight iteration) พร้อมการคำนวณออกแบบเหล็กเสริมและเหล็กปลอกตามหลักวิศวกรรม")
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
        mat_db = {
            "เหล็กรูปพรรณ SS400 (โครงสร้างทั่วไป)": [1440.0, 7850.0, 2.0e6],
            "เหล็กรูปพรรณ SM400 (งานเชื่อมโครงสร้าง)": [1440.0, 7850.0, 2.0e6],
            "เหล็กรูปพรรณกำลังสูง SM490": [1980.0, 7850.0, 2.0e6],
            "ไม้เนื้อแข็ง (เช่น ไม้เต็ง, ไม้แดง)": [120.0, 800.0, 1.0e5],
            "ไม้เนื้ออ่อน (เช่น ไม้ยาง)": [60.0, 600.0, 1.0e5]
        }
        selected_mat = st.selectbox("เลือกประเภทวัสดุ", list(mat_db.keys()), key="mat_homo")
        sigma_allow, density, E_val = mat_db[selected_mat]
        
        section_shape = st.selectbox("รูปแบบรูปทรงหน้าตัด", ["หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)", "หน้าตัดไวด์แฟลงก์ / เอชบีม (Wide Flange / H-Beam)"], key="shape_homo")
        ratio = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5, key="ratio_homo")
        st.info(f"หน่วยแรงดัดยอมให้ (Fb): **{sigma_allow:,.0f} kg/cm²** | ค่า E: **{E_val:,.0f} kg/cm²**")
    
    if st.button("🚀 ประเมินขนาดและวิเคราะห์คาน", type="primary", key="btn_homo"):
        L_cm = L_homo * 100
        delta_allow = L_cm / 360
        M_applied = (val_load_homo * L_homo**2)/8 if is_uniform_homo else (P_homo * L_homo)/4
        
        auto_resized = False
        max_iter = 1000
        iter_count = 0
        h_final = 10.0  # เริ่มลูปค้นหาขนาดจากพิกัดต่ำสุดที่ 10 ซม.
        
        while iter_count < max_iter:
            iter_count += 1
            b_final = math.ceil(h_final / ratio)
            
            if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)":
                w_self_actual = (b_final / 100) * (h_final / 100) * density
                I_prov = (b_final * h_final**3) / 12
                S_prov = (b_final * h_final**2) / 6
            else:
                # ประมาณการปีกและเอวคานเหล็กดัดแปลงสำเร็จรูป (tf = 6% ของ h, tw = 4% ของ h)
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
        else:
            st.divider()
            st.header("📊 2. สรุปผลการประเมินหน้าตัดขั้นสุดท้าย")
            if auto_resized:
                st.warning(f"🔄 **ระบบปรับขนาดเผื่อน้ำหนักตัวเอง:** รวมน้ำหนักคานเสร็จสิ้นเพิ่มขึ้นอีก {w_self_actual:,.2f} kg/m เพื่อความปลอดภัย")
                
            st.success(f"### 📐 ขนาดที่แนะนำ ({section_shape}): กว้าง {b_final:.0f} ซม. × ลึก {h_final:.0f} ซม.")
            
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

            with st.expander("📝 ดูรายการคำนวณเชิงลึก"):
                st.markdown("### 📌 รายการคำนวณคุณสมบัติหน้าตัด")
                st.markdown(f"**โมเมนต์ดัดสูงสุดดัดรวมน้ำหนักโครงสร้าง:** $M_{{max}} = {M_total:,.2f}$ kg-m")
                st.latex(rf"S_{{{{\text{{req}}}}}} = \frac{{M \cdot 100}}{{\sigma_{{{{\text{{allow}}}}}}}} = {S_req_final:,.2f} \text{{ cm}}^3")
                st.latex(rf"I_{{{{\text{{req}}}}}} = {I_req_final:,.2f} \text{{ cm}}^4")
                st.markdown("**หน้าตัดที่จัดให้จริง (Provided Properties):**")
                st.latex(rf"S_{{{{\text{{provided}}}}}} = {S_prov:,.2f} \text{{ cm}}^3 \ge S_{{{{\text{{req}}}}}} \text{{ (OK)}}")
                st.latex(rf"I_{{{{\text{{provided}}}}}} = {I_prov:,.2f} \text{{ cm}}^4 \ge I_{{{{\text{{req}}}}}} \text{{ (OK)}}")
                
            # ฟังก์ชันเสริม: ดาวน์โหลดรายงาน
            report_homo = f"--- BEAM DESIGN REPORT (HOMOGENEOUS) ---\nMaterial: {selected_mat}\nShape: {section_shape}\nSpan: {L_homo} m\nSection Size: {b_final:.0f}x{h_final:.0f} cm\nM_total: {M_total:,.2f} kg-m\nDeflection: {delta_max:,.3f} cm (Allowable: {delta_allow:,.3f} cm)"
            st.download_button("💾 ดาวน์โหลดรายงานผลการคำนวณ", report_homo, file_name="Beam_Design_Report.txt")

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
        # ฐานข้อมูลเหล็กแกนหลักและเหล็กดีด (WSD วสท.)
        steel_dict = {
            "เหล็กเส้นกลม SR24 (ผิวเรียบ)": [1200.0, 2400.0],
            "เหล็กข้ออ้อย SD30": [1500.0, 3000.0],
            "เหล็กข้ออ้อย SD40": [1700.0, 4000.0],
            "เหล็กข้ออ้อย SD50 (กำลังสูง)": [1700.0, 5000.0]
        }
        selected_steel = st.selectbox("ชั้นคุณภาพเหล็กเสริมหลัก", list(steel_dict.keys()), key="steel_rc")
        fs, fy = steel_dict[selected_steel]
        
        fc_prime = st.selectbox("กำลังอัดของคอนกรีต f'c ทรงกระบอก (ksc)", [180, 210, 240, 280, 320], index=1, key="fc_rc")
        ratio_rc = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b) ของคาน RC", min_value=1.5, value=2.0, step=0.5)

        # คำนวณค่าคงที่ของทฤษฎี Working Stress Design (WSD) แท้จริง
        fc = 0.375 * fc_prime
        Ec = 15100 * math.sqrt(fc_prime)
        Es = 2.04e6
        n_ratio = round(Es / Ec)
        k_wsd = n_ratio / (n_ratio + (fs / fc))
        j_wsd = 1.0 - (k_wsd / 3.0)
        R_wsd = 0.5 * fc * k_wsd * j_wsd
        
        st.info(f"**WSD Constants:** n = {n_ratio} | k = {k_wsd:.3f} | j = {j_wsd:.3f} | R = {R_wsd:.2f} ksc")

    if st.button("🚀 ประเมินหน้าตัดและเหล็กเสริม (RC)", type="primary", key="btn_rc"):
        L_cm_rc = L_rc * 100
        delta_allow_rc = L_cm_rc / 360
        auto_resized_rc = False
        max_iter_rc = 1000
        iter_rc_count = 0
        h_rc = 20.0  # เริ่มต้นความลึกที่ 20 ซม.
        
        while iter_rc_count < max_iter_rc:
            iter_rc_count += 1
            b_rc = math.ceil((h_rc / ratio_rc) / 5.0) * 5
            if b_rc < 15: b_rc = 15.0 # หน้าตัดเสา/คานบ้านทั่วไปกว้างไม่ควรน้อยกว่า 15 ซม.
            
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
            d_rc = h_rc - 5.0 # ระยะคอนกรีตหุ้มเคลียร์ริ่งโดยประมาณ
            
            # ตรวจสอบโมเมนต์ยอมให้ด้านหน้าตัดคอนกรีตอัด (Balanced capacity control)
            M_concrete_capacity = (R_wsd * b_rc * d_rc**2) / 100 # หน่วย kg-m
            
            if I_g >= I_req_rc and M_concrete_capacity >= M_total_rc:
                if is_uniform_rc:
                    delta_max_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g)
                else:
                    delta_max_rc = ((P_rc * L_cm_rc**3) / (48 * Ec * I_g)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g))
                break
            else:
                auto_resized_rc = True
                h_rc += 5.0 # เพิ่มขนาดคาน RC ทีละ 5 ซม. ตามแบบสากลช่างก่อสร้าง
                
        if iter_rc_count >= max_iter_rc:
             st.error("⚠️ ไม่สามารถประเมินหน้าตัดคาน RC ได้เนื่องจากน้ำหนักกระทำสูงเกินเกณฑ์ขีดจำกัด")
        else:
            # คำนวณหาพื้นที่เหล็กเสริมรับแรงดึงที่ต้องการ (As)
            As_req = (M_total_rc * 100) / (fs * j_wsd * d_rc)
            # เช็คปริมาณเหล็กเสริมต่ำสุดเพื่อต้านร้าว (Minimum Reinforcement Limit)
            As_min = (14.0 / fy) * b_rc * d_rc
            As_final = max(As_req, As_min)
            
            n_DB12 = math.ceil(As_final / 1.13)
            n_DB16 = math.ceil(As_final / 2.01)
            n_DB20 = math.ceil(As_final / 3.14)
            
            # --- ส่วนขยาย PRO: การออกแบบเหล็กปลอกรับแรงเฉือน (Stirrup Design) ---
            v_v = V_max_rc / (b_rc * d_rc) # หน่วยแรงเฉือนที่เกิดขึ้นจริง (ksc)
            v_c = 0.29 * math.sqrt(fc_prime) # หน่วยแรงเฉือนยอมให้สำหรับคอนกรีต
            
            stirrup_bar = "RB6" if h_rc <= 40 else "RB9"
            Av = 2 * 0.283 if stirrup_bar == "RB6" else 2 * 0.636 # เหล็กปลอก 2 ขา (2-legs stirrup)
            fv_stirrup = 1200.0 # เหล็กปลอก SR24
            
            if v_v <= v_c:
                stirrup_text = f"คอนกรีตรับแรงเฉือนได้พอ แนะนำใส่เหล็กปลอกเหล็กเสริมกันร้าวขั้นต่ำ"
                s_spacing = min(d_rc / 2, 30.0)
            else:
                v_s = v_v - v_c
                v_max_allow = 1.32 * math.sqrt(fc_prime)
                if v_s > v_max_allow:
                    stirrup_text = "⚠️ หน้าตัดเล็กเกินไปสำหรับแรงเฉือน กรุณาขยายขนาดคานเพิ่มด้วยตนเอง"
                    s_spacing = 0
                else:
                    stirrup_text = f"ต้องเสริมเหล็กปลอกเพื่อช่วยรับแรงเฉือนส่วนเกิน"
                    s_spacing = (Av * fv_stirrup) / (v_s * b_rc)
                    s_spacing = min(s_spacing, d_rc / 2, 30.0)
            
            s_spacing_final = math.floor(s_spacing) if s_spacing > 0 else 0

            st.divider()
            st.header("📊 2. สรุปผลการประเมินคานคอนกรีตเสริมเหล็ก")
            if auto_resized_rc:
                st.warning(f"🔄 **ระบบปรับขยายหน้าตัดเพิ่ม:** เนื่องจากขนาดเริ่มต้นไม่ผ่านเกณฑ์การยุบตัว หรือคอนกรีตเกิดหน่วยแรงอัดเกินพิกัด Balanced Design")
                
            st.success(f"### 📐 หน้าตัดคาน RC ที่แนะนำ: กว้าง {b_rc:.0f} ซม. × ลึก {h_rc:.0f} ซม.")
            
            c_out1, c_out2, c_out3 = st.columns(3)
            c_out1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total_rc:,.2f} kg-m")
            c_out2.metric("พื้นที่เหล็กแกนดึงที่ต้องการ (As)", f"{As_final:,.2f} cm²", delta=f"เหล็กขั้นต่ำ {As_min:.2f} cm²")
            c_out3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max_rc:,.3f} cm", delta=f"ยอมให้ {delta_allow_rc:,.2f} cm")
            
            st.info(f"**🛠️ ข้อเสนอแนะการจัดปริมาณเหล็กแกนหลัก:**\n- ใช้เหล็กข้ออ้อย **DB12** จำนวน **{max(2, n_DB12)} เส้น** หรือ\n- ใช้เหล็กข้ออ้อย **DB16** จำนวน **{max(2, n_DB16)} เส้น** หรือ\n- ใช้เหล็กข้ออ้อย **DB20** จำนวน **{max(2, n_DB20)} เส้น**")
            
            if s_spacing_final > 0:
                st.warning(f"**🛡️ การจัดเหล็กปลอกรับแรงเฉือน (Stirrup):** {stirrup_text} แนะนำใช้ **{stirrup_bar} @ {s_spacing_final} ซม.**")
            else:
                st.error(f"**🛡️ การจัดเหล็กปลอกรับแรงเฉือน (Stirrup):** {stirrup_text}")
                
            st.divider()
            st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
            fig_v_rc, fig_m_rc = plot_diagrams(L_rc, w_total_rc, P_rc, is_uniform_rc)
            cr1, cr2 = st.columns(2)
            cr1.plotly_chart(fig_v_rc, use_container_width=True)
            cr2.plotly_chart(fig_m_rc, use_container_width=True)

            with st.expander("📝 ดูรายการคำนวณสูตรแปรผันอย่างละเอียด (WSD)"):
                st.markdown("### 📌 ขั้นตอนวิเคราะห์กำลังหน้าตัดคอนกรีต")
                st.markdown(f"หน่วยแรงอัดคอนกรีตยอมให้: $f_c = 0.375 \\times {fc_prime} = {fc:.2f}$ ksc")
                st.markdown(f"คำนวณสัดส่วนค่า $k = {k_wsd:.3f}$ และค่า แขนของแรง $j = {j_wsd:.3f}$")
                st.latex(rf"M_{{concrete}} = \frac{{R \cdot b \cdot d^2}}{{100}} = \frac{{{R_wsd:.2f} \cdot {b_rc} \cdot {d_rc}^2}}{{100}} = {M_concrete_capacity:,.2f} \text{{ kg-m}}")
                st.latex(rf"A_s = \frac{{M \cdot 100}}{{f_s \cdot j \cdot d}} = {As_req:,.2f} \text{{ cm}}^2")
                st.markdown(f"**การตรวจสอบแรงเฉือน:** แรงเฉือนสูงสุดที่เกิดขึ้นจริง $V_{{max}} = {V_max_rc:,.2f}$ kg")
                st.latex(rf"v_v = \frac{{V_{{max}}}}{{b \cdot d}} = {v_v:.2f} \text{{ ksc}} \quad [v_c = {v_c:.2f} \text{{ ksc}}]")
                
            report_rc = f"--- RC BEAM DESIGN REPORT ---\nConcrete f'c: {fc_prime} ksc\nSteel Grade: {selected_steel}\nSpan: {L_rc} m\nRecommended Section: {b_rc:.0f}x{h_rc:.0f} cm\nRequired As: {As_final:.2f} cm2\nStirrup: {stirrup_bar} @ {s_spacing_final} cm"
            st.download_button("💾 ดาวน์โหลดรายงานผลการคำนวณคาน RC", report_rc, file_name="RC_Beam_Report.txt")
