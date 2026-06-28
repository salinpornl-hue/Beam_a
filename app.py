import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Beam Design Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น (Pro Version)")
st.markdown("ระบบวิเคราะห์หน้าตัดคาน พร้อมรายการคำนวณละเอียดแบบ (ทฤษฎีอธิบาย -> แทนค่า -> ผลลัพธ์)")
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

tab1, tab2 = st.tabs(["🪵 เหล็กรูปพรรณ / ไม้", "🧱 คอนกรีตเสริมเหล็ก (RC Beam)"])

# ==========================================
# TAB 1: เหล็กรูปพรรณ และ ไม้
# ==========================================
with tab1:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (เหล็ก/ไม้)")
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
            "เหล็กรูปพรรณ SS400 (ทั่วไป)": [1440.0, 7850.0, 2.0e6],
            "เหล็กรูปพรรณ SM400 (งานเชื่อม)": [1440.0, 7850.0, 2.0e6],
            "เหล็กรูปพรรณกำลังสูง SM490": [1980.0, 7850.0, 2.0e6],
            "ไม้เนื้อแข็ง": [120.0, 800.0, 1.0e5],
            "ไม้เนื้ออ่อน": [60.0, 600.0, 1.0e5]
        }
        selected_mat = st.selectbox("เลือกประเภทวัสดุ", list(mat_db.keys()), key="mat_homo")
        sigma_allow, density, E_val = mat_db[selected_mat]
        Yield_stress = sigma_allow / 0.6  
        tau_allow = 0.4 * Yield_stress    
        
        section_shape = st.selectbox("รูปแบบรูปทรงหน้าตัด", ["หน้าตัดไวด์แฟลงก์ / เอชบีม (Wide Flange / H-Beam)", "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)"], key="shape_homo")
        
        tw_manual, tf_manual = None, None 

        if "Auto" in design_mode_homo:
            ratio = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5, key="ratio_homo")
            b_manual_homo, h_manual_homo = 0, 0
        else:
            if section_shape == "หน้าตัดไวด์แฟลงก์ / เอชบีม (Wide Flange / H-Beam)":
                c_sec1, c_sec2 = st.columns(2)
                h_manual_homo = c_sec1.number_input("ความลึกคาน H (cm)", min_value=5.0, value=20.0, step=1.0)
                b_manual_homo = c_sec2.number_input("ความกว้างปีก B (cm)", min_value=5.0, value=10.0, step=1.0)
                c_sec3, c_sec4 = st.columns(2)
                tw_manual = c_sec3.number_input("ความหนาเอว tw (mm)", min_value=1.0, value=5.5, step=0.5) / 10.0 
                tf_manual = c_sec4.number_input("ความหนาปีก tf (mm)", min_value=1.0, value=8.0, step=0.5) / 10.0 
                ratio = h_manual_homo / b_manual_homo if b_manual_homo > 0 else 2.0
            else:
                col_b, col_h = st.columns(2)
                b_manual_homo = col_b.number_input("ความกว้าง b (cm)", min_value=1.0, value=15.0, step=1.0, key="b_manual_homo")
                h_manual_homo = col_h.number_input("ความลึก h (cm)", min_value=1.0, value=30.0, step=1.0, key="h_manual_homo")
                ratio = h_manual_homo / b_manual_homo if b_manual_homo > 0 else 2.0

        st.info(f"หน่วยแรงดัด (Fb): **{sigma_allow:,.0f} ksc** | แรงเฉือน (Fv): **{tau_allow:,.0f} ksc**")
    
    if st.button("🚀 ประเมินขนาดและวิเคราะห์คาน", type="primary", key="btn_homo"):
        L_cm = L_homo * 100
        delta_allow = L_cm / 360
        M_applied = (val_load_homo * L_homo**2)/8 if is_uniform_homo else (P_homo * L_homo)/4
        
        auto_resized = False
        is_safe = True
        
        def calc_section(b, h, tw_val=None, tf_val=None):
            if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)":
                w_s = (b / 100) * (h / 100) * density
                I_p = (b * h**3) / 12
                S_p = (b * h**2) / 6
                out_tw, out_tf = 0, 0
            else:
                out_tf = tf_val if tf_val is not None else 0.06 * h
                out_tw = tw_val if tw_val is not None else 0.04 * h
                if 2 * out_tf >= h: out_tf = h * 0.4
                if out_tw >= b: out_tw = b * 0.5
                area_cm2 = (2 * b * out_tf) + ((h - 2 * out_tf) * out_tw)
                w_s = (area_cm2 / 10000) * density
                I_p = (b * h**3 / 12) - ((b - out_tw) * (h - 2 * out_tf)**3 / 12)
                S_p = I_p / (h / 2)
            return w_s, I_p, S_p, out_tw, out_tf

        if "Auto" in design_mode_homo:
            h_final = 10.0  
            while True:
                b_final = math.ceil(h_final / ratio)
                w_self_actual, I_prov, S_prov, tw, tf = calc_section(b_final, h_final)
                w_total_actual = val_load_homo + w_self_actual if is_uniform_homo else w_self_actual
                M_total = M_applied + (w_self_actual * L_homo**2) / 8
                
                S_req_iter = (M_total * 100) / sigma_allow
                if is_uniform_homo:
                    I_req_iter = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * delta_allow)
                else:
                    I_req_iter = ((P_homo * L_cm**3) / (48 * E_val * delta_allow)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * delta_allow))
                    
                if S_prov >= S_req_iter and I_prov >= I_req_iter:
                    break
                h_final += 1.0
                auto_resized = True
                if h_final > 200: 
                    is_safe = False; break
        else:
            b_final, h_final = b_manual_homo, h_manual_homo
            w_self_actual, I_prov, S_prov, tw, tf = calc_section(b_final, h_final, tw_manual, tf_manual)
            w_total_actual = val_load_homo + w_self_actual if is_uniform_homo else w_self_actual
            M_total = M_applied + (w_self_actual * L_homo**2) / 8
            
            S_req_iter = (M_total * 100) / sigma_allow
            if is_uniform_homo:
                I_req_iter = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * delta_allow)
            else:
                I_req_iter = ((P_homo * L_cm**3) / (48 * E_val * delta_allow)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * delta_allow))
                
            if S_prov < S_req_iter or I_prov < I_req_iter:
                is_safe = False

        S_req_final, I_req_final = S_req_iter, I_req_iter
        V_max_homo = (w_total_actual * L_homo / 2) if is_uniform_homo else ((P_homo / 2) + (w_self_actual * L_homo / 2))
        fv_actual = V_max_homo / (h_final * tw) if tw > 0 else 0
        shear_safe = True if (tw == 0 or fv_actual <= tau_allow) else False
        if not shear_safe: is_safe = False

        if is_uniform_homo:
            delta_max = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * I_prov)
        else:
            delta_max = ((P_homo * L_cm**3) / (48 * E_val * I_prov)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * I_prov))

        st.divider()
        st.header("📊 2. สรุปผลการประเมินหน้าตัด")
        
        if not is_safe and "Manual" in design_mode_homo:
            st.error(f"❌ **ขนาดหน้าตัดไม่ปลอดภัย!** รับแรงดัด (S), การแอ่นตัว (I) หรือแรงเฉือน (Fv) ไม่เพียงพอ")
        elif is_safe:
            st.success(f"### 📐 ขนาดที่ใช้: กว้าง {b_final:.0f} ซม. × ลึก {h_final:.0f} ซม.")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total:,.2f} kg-m")
        col_r2.metric("น้ำหนักตัวเอง (Self-Weight)", f"{w_self_actual:,.2f} kg/m")
        col_r3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max:,.3f} cm", delta=f"ยอมให้ {delta_allow:,.3f} cm", delta_color="normal" if delta_max <= delta_allow else "inverse")
            
        st.divider()
        st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
        fig_v, fig_m = plot_diagrams(L_homo, w_total_actual, P_homo, is_uniform_homo)
        cp1, cp2 = st.columns(2)
        cp1.plotly_chart(fig_v, use_container_width=True)
        cp2.plotly_chart(fig_m, use_container_width=True)

        with st.expander("📝 ดูรายการคำนวณแบบละเอียด (ทฤษฎีอธิบาย -> แทนค่า -> ผลลัพธ์)"):
            st.markdown("### 📌 ขั้นตอนที่ 1: คำนวณแรงภายในคาน (Design Forces)")
            if is_uniform_homo:
                st.latex(rf"M_{{max}} = \frac{{w_{{total}} L^2}}{{8}} = \frac{{{w_total_actual:,.2f} \cdot {L_homo}^2}}{{8}} = {M_total:,.2f} \text{{ kg-m}}")
                st.latex(rf"V_{{max}} = \frac{{w_{{total}} L}}{{2}} = \frac{{{w_total_actual:,.2f} \cdot {L_homo}}}{{2}} = {V_max_homo:,.2f} \text{{ kg}}")
            else:
                st.latex(rf"M_{{max}} = \frac{{P L}}{{4}} + \frac{{w_{{self}} L^2}}{{8}} = \frac{{{P_homo} \cdot {L_homo}}}{{4}} + \frac{{{w_self_actual:,.2f} \cdot {L_homo}^2}}{{8}} = {M_total:,.2f} \text{{ kg-m}}")
                st.latex(rf"V_{{max}} = \frac{{P}}{{2}} + \frac{{w_{{self}} L}}{{2}} = \frac{{{P_homo}}}{{2}} + \frac{{{w_self_actual:,.2f} \cdot {L_homo}}}{{2}} = {V_max_homo:,.2f} \text{{ kg}}")
            
            st.markdown("---")
            st.markdown(r"### 📌 ขั้นตอนที่ 2: การหาค่าความต้องการของหน้าตัด (Required Section Properties)")
            st.markdown(r"ในการออกแบบคาน หน้าตัดจะต้องมีขนาดใหญ่พอที่จะต้านทาน **โมเมนต์ดัด (Bending Moment)** ไม่ให้วัสดุเกิดความเค้นเกินขีดจำกัด และต้องมีสติฟเนส (Stiffness) มากพอที่จะต้านทาน **การแอ่นตัว (Deflection)** ไม่ให้เกินค่าที่มาตรฐานกำหนด")
            
            st.markdown(r"**2.1 ความต้องการเพื่อต้านทานการดัด (Bending Criteria):**")
            st.markdown(r"จากทฤษฎีแรงดัด (Flexure Formula) หน่วยแรงดัดดึง/อัดสูงสุด คำนวณจาก $\sigma = \frac{M \cdot c}{I}$ และเนื่องจาก Section Modulus ถูกนิยามไว้ว่า $S = \frac{I}{c}$ สมการจึงเขียนได้เป็น $\sigma = \frac{M}{S}$")
            st.markdown(r"ดังนั้น เพื่อไม่ให้หน่วยแรงที่เกิดขึ้นจริงเกินค่าความเค้นที่ยอมให้ ($\sigma_{allow}$) คานจึงต้องการค่า $S_{req}$ ขั้นต่ำดังนี้:")
            st.latex(rf"S_{{req}} = \frac{{M_{{max}} \cdot 100 \text{{ (แปลงหน่วย)}}}}{{F_b}} = \frac{{{M_total:,.2f} \cdot 100}}{{{sigma_allow:,.0f}}} = {S_req_final:,.2f} \text{{ cm}}^3")
            
            st.markdown(r"**2.2 ความต้องการเพื่อควบคุมการแอ่นตัว (Deflection Criteria):**")
            st.markdown(r"มาตรฐานทางวิศวกรรมทั่วไปกำหนดให้คานรับน้ำหนักใช้งาน (Service Load) แอ่นตัวได้สูงสุดไม่เกิน $L/360$ ของความยาวช่วงคาน:")
            st.latex(rf"\Delta_{{allow}} = \frac{{L}}{{360}} = \frac{{{L_cm:,.0f}}}{{360}} = {delta_allow:,.3f} \text{{ cm}}")
            
            st.markdown(r"จากสมการการแอ่นตัวของคาน (Elastic Curve) เราสามารถย้ายข้างสมการเพื่อหาค่าโมเมนต์ความเฉื่อย ($I_{req}$) ขั้นต่ำที่สอดคล้องกับ $\Delta_{allow}$ ได้:")
            if is_uniform_homo:
                st.markdown(r"- กรณี **น้ำหนักแผ่กระจายสม่ำเสมอ (Uniform Load):** สูตรการแอ่นตัวสูงสุดคือ $\Delta = \frac{5wL^4}{384EI}$")
                st.latex(rf"I_{{req}} = \frac{{5 \cdot w_{{total}} \cdot L^4}}{{384 \cdot E \cdot \Delta_{{allow}}}} = \frac{{5 \cdot ({w_total_actual:,.2f}/100) \cdot {L_cm:,.0f}^4}}{{384 \cdot {E_val:,.0f} \cdot {delta_allow:,.3f}}} = {I_req_final:,.2f} \text{{ cm}}^4")
            else:
                st.markdown(r"- กรณี **น้ำหนักกระทำเป็นจุดกึ่งกลาง (Point Load) + น้ำหนักคาน (Uniform):** ใช้หลักการ Superposition $\Delta = \frac{PL^3}{48EI} + \frac{5w_{self}L^4}{384EI}$")
                st.latex(rf"I_{{req}} = \left(\frac{{P L^3}}{{48 E \Delta_{{allow}}}}\right) + \left(\frac{{5 w_{{self}} L^4}}{{384 E \Delta_{{allow}}}}\right) = \left(\frac{{{P_homo:,.0f} \cdot {L_cm:,.0f}^3}}{{48 \cdot {E_val:,.0f} \cdot {delta_allow:,.3f}}}\right) + \left(\frac{{5 \cdot ({w_self_actual:,.2f}/100) \cdot {L_cm:,.0f}^4}}{{384 \cdot {E_val:,.0f} \cdot {delta_allow:,.3f}}}\right) = {I_req_final:,.2f} \text{{ cm}}^4")

            if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)":
                b_min_bend_final = math.pow((6 * S_req_final) / (ratio**2), 1/3) 
                b_min_def_final = math.pow((12 * I_req_final) / (ratio**3), 0.25) 
                b_req_theoretical = max(b_min_bend_final, b_min_def_final)
                h_req_theoretical = b_req_theoretical * ratio
                
                st.markdown("---")
                st.markdown(r"### 📌 ขั้นตอนที่ 3: การถอดสมการหาความกว้าง (b) และความลึก (h) ขั้นต่ำสุดทางทฤษฎี")
                st.markdown(rf"เมื่อเราทราบว่าหน้าตัดเป็นรูปสี่เหลี่ยมตัน และได้กำหนดสัดส่วนความลึกต่อความกว้างไว้เป็น $h = {ratio}b$ เราสามารถนำสัดส่วนนี้ไปแทนค่าในสูตรคุณสมบัติหน้าตัด เพื่อจัดรูปสมการหาค่าความกว้าง $b$ ขั้นต่ำได้ดังนี้:")
                
                st.markdown(r"**3.1 ขนาดหน้าตัดขั้นต่ำจากเกณฑ์โมเมนต์ดัด:**")
                st.markdown(rf"สูตร Section Modulus ของหน้าตัดสี่เหลี่ยมคือ $S = \frac{{bh^2}}{{6}}$ เมื่อแทนค่า $h = {ratio}b$ จะได้ $S = \frac{{{ratio**2} \cdot b^3}}{{6}}$ ย้ายข้างสมการเพื่อหา $b$:")
                st.latex(rf"b \ge \sqrt[3]{{\frac{{6 \cdot S_{{req}}}}{{{ratio**2}}}}} \implies \sqrt[3]{{\frac{{6 \cdot {S_req_final:,.2f}}}{{{ratio**2}}}}} \implies b \ge {b_min_bend_final:,.2f} \text{{ cm}}")

                st.markdown(r"**3.2 ขนาดหน้าตัดขั้นต่ำจากเกณฑ์การแอ่นตัว:**")
                st.markdown(rf"สูตร Moment of Inertia ของหน้าตัดสี่เหลี่ยมคือ $I = \frac{{bh^3}}{{12}}$ เมื่อแทนค่า $h = {ratio}b$ จะได้ $I = \frac{{{ratio**3} \cdot b^4}}{{12}}$ ย้ายข้างสมการเพื่อหา $b$:")
                st.latex(rf"b \ge \sqrt[4]{{\frac{{12 \cdot I_{{req}}}}{{{ratio**3}}}}} \implies \sqrt[4]{{\frac{{12 \cdot {I_req_final:,.2f}}}{{{ratio**3}}}}} \implies b \ge {b_min_def_final:,.2f} \text{{ cm}}")
                
                st.markdown(rf"**สรุปการหาค่าตามทฤษฎี:** ต้องเลือกค่า $b$ ที่สูงกว่า เพื่อให้หน้าตัดผ่านทั้งสองเกณฑ์ $\implies b_{{min}} = {b_req_theoretical:,.2f}$ cm")
                st.markdown(rf"และเมื่อนำไปหาค่าความลึก จะได้ $h_{{min}} = {ratio} \times {b_req_theoretical:,.2f} = {h_req_theoretical:,.2f}$ cm")

            st.markdown("---")
            st.markdown("### 📌 ขั้นตอนที่ 4: สรุปการตรวจสอบหน้าตัดใช้งาน (Section Verification)")
            pass_S = "OK (ปลอดภัย)" if S_prov >= S_req_final else "NG (ไม่ผ่าน)"
            st.markdown(f"**1. ตรวจสอบพิกัดต้านทานการดัด ($S_{{prov}} = {S_prov:,.2f}$ cm³):**")
            st.latex(rf"S_{{prov}} \ge S_{{req}} \implies {S_prov:,.2f} \ge {S_req_final:,.2f} \implies \text{{{pass_S}}}")
            
            pass_I = "OK (ปลอดภัย)" if I_prov >= I_req_final else "NG (ไม่ผ่าน)"
            st.markdown(f"**2. ตรวจสอบการแอ่นตัว ($I_{{prov}} = {I_prov:,.2f}$ cm⁴):**")
            st.latex(rf"I_{{prov}} \ge I_{{req}} \implies {I_prov:,.2f} \ge {I_req_final:,.2f} \implies \text{{{pass_I}}}")
            
            if "Wide" in section_shape:
                pass_V = "OK (ปลอดภัย)" if fv_actual <= tau_allow else "NG (ไม่ผ่าน)"
                st.markdown("**3. ตรวจสอบหน่วยแรงเฉือนในเอวคาน (Web Shear Check):**")
                st.latex(rf"f_v = \frac{{V_{{max}}}}{{h \cdot t_w}} = \frac{{{V_max_homo:,.2f}}}{{{h_final:.2f} \cdot {tw:.2f}}} = {fv_actual:,.2f} \text{{ ksc}}")
                st.latex(rf"f_v \le F_v \implies {fv_actual:,.2f} \le {tau_allow:,.2f} \implies \text{{{pass_V}}}")

# ==========================================
# TAB 2: คอนกรีตเสริมเหล็ก (RC Beam)
# ==========================================
with tab2:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (คาน RC)")
    design_mode_rc = st.radio("โหมดการออกแบบ (RC Beam)", ["🔍 คำนวณขนาดอัตโนมัติ (Auto-sizing)", "✍️ กำหนดขนาดเอง (Manual)"], horizontal=True, key="mode_rc")
    
    st.markdown("---")
    rc_shape = st.selectbox("📌 รูปแบบหน้าตัดคานคอนกรีต", ["คานสี่เหลี่ยมผืนผ้า (Rectangular Beam)", "คานรูปตัวที (T-Beam)"], key="rc_shape")
    
    if rc_shape == "คานรูปตัวที (T-Beam)":
        col_t1, col_t2 = st.columns(2)
        bf_rc = col_t1.number_input("ความกว้างปีกคาน (bf) (cm)", min_value=10.0, value=100.0, step=10.0)
        hf_rc = col_t2.number_input("ความหนาปีกคาน/พื้น (hf) (cm)", min_value=5.0, value=10.0, step=1.0)
    else:
        bf_rc = 0; hf_rc = 0
        
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
        steel_dict = {"เหล็กเส้นกลม SR24": [1200.0, 2400.0], "เหล็กข้ออ้อย SD30": [1500.0, 3000.0], "เหล็กข้ออ้อย SD40": [1700.0, 4000.0]}
        selected_steel = st.selectbox("ชั้นคุณภาพเหล็กเสริมหลัก", list(steel_dict.keys()), key="steel_rc")
        fs, fy = steel_dict[selected_steel]
        fc_prime = st.selectbox("กำลังอัดคอนกรีต f'c (ksc)", [180, 210, 240, 280, 320], index=1, key="fc_rc")
        
        if "Auto" in design_mode_rc:
            ratio_rc = st.number_input("สัดส่วน h/bw ของคาน", min_value=1.5, value=2.0, step=0.5)
            b_manual_rc, h_manual_rc = 0, 0
        else:
            c_rc_b, c_rc_h = st.columns(2)
            b_manual_rc = c_rc_b.number_input("ความกว้างเอวคาน bw (cm)", min_value=10.0, value=20.0, step=5.0)
            h_manual_rc = c_rc_h.number_input("ความลึกคานรวม h (cm)", min_value=10.0, value=40.0, step=5.0)
            ratio_rc = h_manual_rc / b_manual_rc if b_manual_rc > 0 else 2.0

        fc = 0.375 * fc_prime
        Ec = 15100 * math.sqrt(fc_prime)
        n_ratio = round(2.04e6 / Ec)
        k_wsd = n_ratio / (n_ratio + (fs / fc))
        j_val = 1.0 - (k_wsd / 3.0)
        R_wsd = 0.5 * fc * k_wsd * j_val

    if st.button("🚀 ประเมินหน้าตัดและเหล็กเสริม (RC)", type="primary", key="btn_rc"):
        L_cm_rc = L_rc * 100
        delta_allow_rc = L_cm_rc / 360
        is_rc_safe = True
        
        def calc_rc_properties(bw, h):
            d = h - 5.0
            if rc_shape == "คานรูปตัวที (T-Beam)":
                w_self = (bw / 100) * ((h - hf_rc) / 100) * 2400 if h > hf_rc else 0
                A1 = bf_rc * hf_rc
                A2 = bw * (h - hf_rc) if h > hf_rc else 0
                if A1 + A2 > 0:
                    y_bar = (A1 * (hf_rc / 2) + A2 * (hf_rc + (h - hf_rc)/2)) / (A1 + A2)
                    Ig_1 = (bf_rc * hf_rc**3)/12 + A1 * (y_bar - hf_rc/2)**2
                    Ig_2 = (bw * (h - hf_rc)**3)/12 + A2 * (hf_rc + (h - hf_rc)/2 - y_bar)**2 if h > hf_rc else 0
                    Ig = Ig_1 + Ig_2
                else:
                    Ig = 1
                Mc = (R_wsd * bf_rc * d**2) / 100 
            else:
                w_self = (bw / 100) * (h / 100) * 2400
                Ig = (bw * h**3) / 12
                Mc = (R_wsd * bw * d**2) / 100
            return w_self, Ig, Mc, d

        if "Auto" in design_mode_rc:
            h_rc = math.ceil((L_cm_rc / 10.0) / 5.0) * 5
            while True:
                bw_rc = math.ceil((h_rc / ratio_rc) / 5.0) * 5
                if bw_rc < 15: bw_rc = 15.0 
                
                w_self_rc, I_g, M_concrete_capacity, d_rc = calc_rc_properties(bw_rc, h_rc)
                
                if is_uniform_rc:
                    w_total_rc = val_load_rc + w_self_rc
                    M_total_rc = (w_total_rc * L_rc**2) / 8
                    I_req_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc)
                else:
                    w_total_rc = w_self_rc
                    M_total_rc = (P_rc * L_rc) / 4 + (w_self_rc * L_rc**2) / 8
                    I_req_rc = ((P_rc * L_cm_rc**3) / (48 * Ec * delta_allow_rc)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc))
                    
                if I_g >= I_req_rc and M_concrete_capacity >= M_total_rc:
                    break
                h_rc += 5.0 
                if h_rc > 200:
                    is_rc_safe = False; break
        else:
            bw_rc, h_rc = b_manual_rc, h_manual_rc
            w_self_rc, I_g, M_concrete_capacity, d_rc = calc_rc_properties(bw_rc, h_rc)
            
            if is_uniform_rc:
                w_total_rc = val_load_rc + w_self_rc
                M_total_rc = (w_total_rc * L_rc**2) / 8
                I_req_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc)
            else:
                w_total_rc = w_self_rc
                M_total_rc = (P_rc * L_rc) / 4 + (w_self_rc * L_rc**2) / 8
                I_req_rc = ((P_rc * L_cm_rc**3) / (48 * Ec * delta_allow_rc)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * delta_allow_rc))
                
            if I_g < I_req_rc or M_concrete_capacity < M_total_rc:
                is_rc_safe = False

        if "is_rc_safe" in locals():
            As_req = (M_total_rc * 100) / (fs * j_val * d_rc) if d_rc > 0 else 0
            As_min = (14.0 / fy) * bw_rc * d_rc
            As_final = max(As_req, As_min)
            n_DB12 = math.ceil(As_final / 1.13)
            n_DB16 = math.ceil(As_final / 2.01)
            
            V_max_rc = (w_total_rc * L_rc / 2) if is_uniform_rc else (P_rc / 2 + w_self_rc * L_rc / 2)
            v_v = V_max_rc / (bw_rc * d_rc) if bw_rc*d_rc > 0 else 0
            v_c = 0.29 * math.sqrt(fc_prime) 
            stirrup_bar = "RB6" if h_rc <= 40 else "RB9"
            Av = 2 * 0.283 if stirrup_bar == "RB6" else 2 * 0.636
            
            if v_v <= v_c:
                stirrup_text = f"คอนกรีตรับแรงเฉือนได้พอ แนะนำใส่เหล็กปลอกกันร้าว"
                s_spacing = min(d_rc / 2, 30.0)
            else:
                v_s = v_v - v_c
                v_max_allow = 1.32 * math.sqrt(fc_prime)
                if v_s > v_max_allow:
                    stirrup_text = "⚠️ เอวคานเล็กเกินไปสำหรับรับแรงเฉือน!"
                    s_spacing = 0
                    is_rc_safe = False
                else:
                    stirrup_text = f"ต้องเสริมเหล็กปลอกช่วยรับแรงเฉือน"
                    s_spacing = (Av * 1200.0) / (v_s * bw_rc)
                    s_spacing = min(s_spacing, d_rc / 2, 30.0)
            
            s_spacing_final = math.floor(s_spacing) if s_spacing > 0 else 0
            delta_max_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g) if is_uniform_rc else ((P_rc * L_cm_rc**3) / (48 * Ec * I_g)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * Ec * I_g))

            st.divider()
            st.header("📊 2. สรุปผลการประเมินคานคอนกรีตเสริมเหล็ก")
            
            if not is_rc_safe and "Manual" in design_mode_rc:
                st.error(f"❌ **ขนาดคานไม่ปลอดภัย!** อาจจะรับโมเมนต์ดัดไม่ไหว (M > Mc) หรือแอ่นตัวเกิน")
            elif is_rc_safe:
                if rc_shape == "คานรูปตัวที (T-Beam)":
                    st.success(f"### 📐 หน้าตัด (T-Beam): เอวคาน $b_w$ = {bw_rc:.0f} ซม., ลึกรวม $h$ = {h_rc:.0f} ซม.")
                else:
                    st.success(f"### 📐 หน้าตัด (Rectangular): กว้าง {bw_rc:.0f} ซม. × ลึก {h_rc:.0f} ซม.")
            
            c_out1, c_out2, c_out3 = st.columns(3)
            c_out1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total_rc:,.2f} kg-m")
            c_out2.metric("เหล็กแกนดึงที่ต้องการ (As)", f"{As_final:,.2f} cm²", delta=f"เหล็กขั้นต่ำ {As_min:.2f} cm²")
            c_out3.metric("หน่วยแรงเฉือน (v_v)", f"{v_v:,.2f} ksc", delta=f"คอนกรีตรับได้ {v_c:,.2f} ksc", delta_color="normal" if v_v <= v_c else "inverse")
            
            if is_rc_safe or "Manual" in design_mode_rc:
                st.info(f"**🛠️ เหล็กเสริมหลัก:** แนะนำใช้ DB12 จำนวน {max(2, n_DB12)} เส้น หรือ DB16 จำนวน {max(2, n_DB16)} เส้น")
                if s_spacing_final > 0:
                    st.warning(f"**🛡️ เหล็กปลอกรับแรงเฉือน:** {stirrup_text} ใช้ **{stirrup_bar} @ {s_spacing_final} ซม.**")

            with st.expander("📝 ดูรายการคำนวณ RC เจาะลึก (ทฤษฎีอธิบาย -> แทนค่า -> ผลลัพธ์)"):
                st.markdown("### 📌 ขั้นตอนที่ 1: คำนวณแรงภายในคาน (Design Forces)")
                if is_uniform_rc:
                    st.latex(rf"M_{{max}} = \frac{{w_{{total}} L^2}}{{8}} = \frac{{{w_total_rc:,.2f} \cdot {L_rc}^2}}{{8}} = {M_total_rc:,.2f} \text{{ kg-m}}")
                    st.latex(rf"V_{{max}} = \frac{{w_{{total}} L}}{{2}} = \frac{{{w_total_rc:,.2f} \cdot {L_rc}}}{{2}} = {V_max_rc:,.2f} \text{{ kg}}")
                else:
                    st.latex(rf"M_{{max}} = \frac{{P L}}{{4}} + \frac{{w_{{self}} L^2}}{{8}} = \frac{{{P_rc} \cdot {L_rc}}}{{4}} + \frac{{{w_self_rc:,.2f} \cdot {L_rc}^2}}{{8}} = {M_total_rc:,.2f} \text{{ kg-m}}")
                    st.latex(rf"V_{{max}} = \frac{{P}}{{2}} + \frac{{w_{{self}} L}}{{2}} = \frac{{{P_rc}}}{{2}} + \frac{{{w_self_rc:,.2f} \cdot {L_rc}}}{{2}} = {V_max_rc:,.2f} \text{{ kg}}")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 2: ตรวจสอบกำลังของคอนกรีต (Concrete Moment Capacity)")
                b_calc = bf_rc if rc_shape == "คานรูปตัวที (T-Beam)" else bw_rc
                st.latex(rf"d = h - 5 = {h_rc:.0f} - 5 = {d_rc:.2f} \text{{ cm}}")
                st.latex(rf"M_c = \frac{{R \cdot b \cdot d^2}}{{100}} = \frac{{{R_wsd:.2f} \cdot {b_calc:.0f} \cdot {d_rc:.2f}^2}}{{100}} = {M_concrete_capacity:,.2f} \text{{ kg-m}}")
                
                pass_Mc = "OK (คอนกรีตรับแรงอัดไหว)" if M_concrete_capacity >= M_total_rc else "NG (ต้องขยายหน้าตัด)"
                st.latex(rf"M_c \ge M_{{max}} \implies {M_concrete_capacity:,.2f} \ge {M_total_rc:,.2f} \implies \text{{{pass_Mc}}}")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 3: คำนวณหาพื้นที่เหล็กเสริมรับแรงดึง (Required Main Rebar)")
                st.markdown(f"จากหน้าตัดที่เลือก และโมเมนต์ดัดรวม $M_{{total}} = {M_total_rc:,.2f}$ kg-m (ใช้วิธี Working Stress Design):")
                st.latex(rf"A_s = \frac{{M_{{max}} \cdot 100}}{{f_s \cdot j \cdot d}} = \frac{{{M_total_rc:,.2f} \cdot 100}}{{{fs:,.0f} \cdot {j_val:.3f} \cdot {d_rc:.2f}}} = {As_req:,.2f} \text{{ cm}}^2")
                st.latex(rf"A_{{s,min}} = \frac{{14}}{{F_y}} \cdot b_w \cdot d = \frac{{14}}{{{fy:,.0f}}} \cdot {bw_rc:.0f} \cdot {d_rc:.2f} = {As_min:,.2f} \text{{ cm}}^2")
                st.latex(rf"A_{{s,use}} = \max(A_s, A_{{s,min}}) = {As_final:,.2f} \text{{ cm}}^2")

                st.markdown("---")
                st.markdown("### 📌 ขั้นตอนที่ 4: การตรวจสอบและออกแบบเหล็กปลอก (Shear Design)")
                st.markdown(f"แรงเฉือนสูงสุดที่เกิดขึ้นจริง $V_{{max}} = {V_max_rc:,.2f}$ kg")
                st.latex(rf"v_v = \frac{{V_{{max}}}}{{b_w \cdot d}} = \frac{{{V_max_rc:,.2f}}}{{{bw_rc:.0f} \cdot {d_rc:.2f}}} = {v_v:.2f} \text{{ ksc}}")
                st.latex(rf"v_c = 0.29\sqrt{{f'_c}} = 0.29\sqrt{{{fc_prime}}} = {v_c:.2f} \text{{ ksc}}")
                
                if v_v <= v_c:
                    st.markdown(rf"**สรุป:** ค่า $v_v ({v_v:.2f}) \le v_c ({v_c:.2f})$ คอนกรีตสามารถรับแรงเฉือนได้เพียงพอ แนะนำใส่เหล็กปลอกระยะห่างกันร้าว:")
                    st.latex(rf"S_{{max}} = \frac{{d}}{{2}} = \frac{{{d_rc:.2f}}}{{2}} = {d_rc/2:.2f} \text{{ cm}}")
                else:
                    if "v_s" in locals():
                        st.markdown(rf"**สรุป:** ค่า $v_v ({v_v:.2f}) > v_c ({v_c:.2f})$ คอนกรีตรับไม่ไหว ต้องคำนวณเหล็กปลอก (สมมติใช้ {stirrup_bar} 2 ขา, $A_v = {Av:.3f}$ cm²):")
                        st.latex(rf"v_s = v_v - v_c = {v_v:.2f} - {v_c:.2f} = {v_s:.2f} \text{{ ksc}}")
                        st.latex(rf"S = \frac{{A_v \cdot f_v}}{{v_s \cdot b_w}} = \frac{{{Av:.3f} \cdot 1200}}{{{v_s:.2f} \cdot {bw_rc:.0f}}} = {s_spacing:.2f} \text{{ cm}}")
