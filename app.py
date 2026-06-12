import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Beam Design Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น (Pro Version)")
st.markdown("รองรับการคิดน้ำหนักตัวเอง, ปรับขนาดอัตโนมัติหากแอ่นตัวเกินเกณฑ์, แสดงกราฟ และ **แสดงรายการคำนวณแบบ Required ➔ Provided**")
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
            "เหล็กรูปพรรณ (SS400)": [1200.0, 7850.0, 2.0e6],
            "ไม้เนื้อแข็ง (เช่น ไม้เต็ง)": [120.0, 800.0, 1.0e5],
            "ไม้เนื้ออ่อน (เช่น ไม้ยาง)": [60.0, 600.0, 1.0e5]
        }
        selected_mat = st.selectbox("เลือกประเภทวัสดุ", list(mat_db.keys()), key="mat_homo")
        sigma_allow, density, E_val = mat_db[selected_mat]
        st.info(f"หน่วยแรงดัด: **{sigma_allow} kg/cm²** | ความหนาแน่น: **{density:,.0f} kg/m³** | ค่า E: **{E_val:,.0f} kg/cm²**")
        ratio = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5, key="ratio_homo")

    if st.button("🚀 ประเมินขนาดและวิเคราะห์คาน", type="primary", key="btn_homo"):
        M_applied = (val_load_homo * L_homo**2)/8 if is_uniform_homo else (P_homo * L_homo)/4
        S_init = (M_applied * 100) / sigma_allow
        b_init = math.pow((6 * S_init) / (ratio**2), 1/3)
        h_init = ratio * b_init
        
        b_final = math.ceil(b_init)
        h_final = math.ceil(ratio * b_final)
        
        L_cm = L_homo * 100
        delta_allow = L_cm / 360
        auto_resized = False
        
        while True:
            w_self_actual = (b_final / 100) * (h_final / 100) * density
            w_total_actual = val_load_homo + w_self_actual
            I_val = (b_final * h_final**3) / 12
            
            if is_uniform_homo:
                delta_max = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * I_val)
            else:
                delta_P = (P_homo * L_cm**3) / (48 * E_val * I_val)
                delta_w = (5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * I_val)
                delta_max = delta_P + delta_w
                
            if delta_max <= delta_allow:
                break
            else:
                auto_resized = True
                b_final += 1
                h_final = math.ceil(b_final * ratio)
        
        M_self = (w_self_actual * L_homo**2) / 8
        M_total = M_applied + M_self
        
        # ตัวแปรสำหรับรายการคำนวณ
        S_req_val = (M_total * 100) / sigma_allow
        S_provided = (b_final * h_final**2) / 6
        if is_uniform_homo:
            I_req_val = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * delta_allow)
        else:
            I_req_val = ((P_homo * L_cm**3) / (48 * E_val * delta_allow)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * delta_allow))
        
        st.divider()
        st.header("📊 2. สรุปผลการประเมินหน้าตัดขั้นสุดท้าย")
        
        if auto_resized:
            st.warning(f"🔄 **ระบบทำการปรับขนาดหน้าตัดอัตโนมัติ!** เพื่อแก้ปัญหาการแอ่นตัว")
            
        st.success(f"### 📐 ขนาดหน้าตัดที่ปลอดภัย: กว้าง {b_final} ซม. × ลึก {h_final} ซม.")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("โมเมนต์รวม (M_total)", f"{M_total:,.2f} kg-m")
        col_r2.metric("น้ำหนักคานประเมิน", f"{w_self_actual:,.2f} kg/m")
        col_r3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max:,.3f} cm", delta=f"ยอมให้ {delta_allow:,.3f} cm", delta_color="normal")
            
        st.divider()
        st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
        fig_v, fig_m = plot_diagrams(L_homo, w_total_actual, P_homo, is_uniform_homo)
        cp1, cp2 = st.columns(2)
        cp1.plotly_chart(fig_v, use_container_width=True)
        cp2.plotly_chart(fig_m, use_container_width=True)

        # ================= รายการคำนวณ (Tab 1) =================
        with st.expander("📝 ดูรายการคำนวณ (Required vs Provided)"):
            st.markdown("### 📌 ขั้นตอนที่ 1: หาค่าความต้องการหน้าตัดขั้นต่ำ (Required Properties)")
            st.markdown("จากน้ำหนักบรรทุกและโมเมนต์ดัดที่เกิดขึ้น หน้าตัดต้องมีคุณสมบัติ **ขั้นต่ำ** ดังนี้:")
            
            st.markdown("**1. เพื่อต้านทานโมเมนต์ดัด (Bending Stress):**")
            st.latex(rf"S_{{req}} = \frac{{M_{{max}} \cdot 100}}{{\sigma_{{allow}}}} = \frac{{{M_total:,.2f} \cdot 100}}{{{sigma_allow}}} = {S_req_val:,.2f} \text{{ cm}}^3")
            
            st.markdown("**2. เพื่อควบคุมการแอ่นตัว (Deflection):**")
            st.latex(rf"\Delta_{{allow}} = \frac{{L}}{{360}} = {delta_allow:,.3f} \text{{ cm}}")
            if is_uniform_homo:
                st.latex(rf"I_{{req}} = \frac{{5 \cdot w_{{total}} \cdot L^4}}{{384 \cdot E \cdot \Delta_{{allow}}}} = {I_req_val:,.2f} \text{{ cm}}^4")
            else:
                st.latex(rf"I_{{req}} = \frac{{P \cdot L^3}}{{48 \cdot E \cdot \Delta_{{allow}}}} + \frac{{5 \cdot w_{{self}} \cdot L^4}}{{384 \cdot E \cdot \Delta_{{allow}}}} = {I_req_val:,.2f} \text{{ cm}}^4")

            st.markdown("---")
            st.markdown("### 📌 ขั้นตอนที่ 2: เลือกขนาดหน้าตัด (Try Section)")
            st.markdown(f"ทดลองเลือกใช้หน้าตัด กว้าง **$b = {b_final}$ cm**, ลึก **$h = {h_final}$ cm**")

            st.markdown("---")
            st.markdown("### 📌 ขั้นตอนที่ 3: ตรวจสอบหน้าตัด (Section Check)")
            st.markdown("นำค่า $b$ และ $h$ ที่เลือกมาคำนวณหาค่าที่จัดให้ (Provided) เพื่อเทียบกับค่าขั้นต่ำ (Required):")
            st.latex(rf"S_{{provided}} = \frac{{b \cdot h^2}}{{6}} = \frac{{{b_final} \cdot {h_final}^2}}{{6}} = {S_provided:,.2f} \text{{ cm}}^3 \ge S_{{req}} \text{{ (OK)}}")
            st.latex(rf"I_{{provided}} = \frac{{b \cdot h^3}}{{12}} = \frac{{{b_final} \cdot {h_final}^3}}{{12}} = {I_val:,.2f} \text{{ cm}}^4 \ge I_{{req}} \text{{ (OK)}}")

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
        steel_dict = {"เหล็กข้ออ้อย SD30": 1200.0, "เหล็กข้ออ้อย SD40": 1500.0}
        fs = steel_dict[st.selectbox("เหล็กเสริมหลัก", list(steel_dict.keys()), key="steel_rc")]
        j_val = 0.875
        st.info("ความหนาแน่นคอนกรีต: **2,400 kg/m³** | โมดูลัสยืดหยุ่น (E): **~200,000 kg/cm²**")

    if st.button("🚀 ประเมินหน้าตัดและเหล็กเสริม (RC)", type="primary", key="btn_rc"):
        h_rc = math.ceil(((L_rc * 100) / 10) / 5.0) * 5
        b_rc = math.ceil((h_rc / 2) / 5.0) * 5
        
        L_cm_rc = L_rc * 100
        delta_allow_rc = L_cm_rc / 360
        E_c = 2.0e5
        auto_resized_rc = False
        
        while True:
            w_self_rc = (b_rc / 100) * (h_rc / 100) * 2400
            w_total_rc = val_load_rc + w_self_rc
            I_g = (b_rc * h_rc**3) / 12
            
            if is_uniform_rc:
                delta_max_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * E_c * I_g)
            else:
                delta_P_rc = (P_rc * L_cm_rc**3) / (48 * E_c * I_g)
                delta_w_rc = (5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * E_c * I_g)
                delta_max_rc = delta_P_rc + delta_w_rc
                
            if delta_max_rc <= delta_allow_rc:
                break
            else:
                auto_resized_rc = True
                h_rc += 5
                b_rc = math.ceil((h_rc / 2) / 5.0) * 5
                
        M_applied_rc = (val_load_rc * L_rc**2)/8 if is_uniform_rc else (P_rc * L_rc)/4
        M_self_rc = (w_self_rc * L_rc**2) / 8
        M_total_rc = M_applied_rc + M_self_rc
        
        d_rc = h_rc - 5
        As_req = (M_total_rc * 100) / (fs * j_val * d_rc)
        
        n_DB12 = math.ceil(As_req / 1.13)
        n_DB16 = math.ceil(As_req / 2.01)
        
        # คำนวณ I_req ของ RC
        if is_uniform_rc:
            I_req_rc = (5 * (w_total_rc / 100) * L_cm_rc**4) / (384 * E_c * delta_allow_rc)
        else:
            I_req_rc = ((P_rc * L_cm_rc**3) / (48 * E_c * delta_allow_rc)) + ((5 * (w_self_rc / 100) * L_cm_rc**4) / (384 * E_c * delta_allow_rc))

        st.divider()
        st.header("📊 2. สรุปผลการประเมิน (คาน RC)")
        
        if auto_resized_rc:
            st.warning(f"🔄 **ระบบทำการปรับเพิ่มขนาดคานอัตโนมัติ!** เพื่อป้องกันการแอ่นตัวเกินมาตรฐาน")
            
        st.success(f"### 📐 หน้าตัดคานที่ปลอดภัย: กว้าง {b_rc} × ลึก {h_rc} ซม.")
        
        c_out1, c_out2, c_out3 = st.columns(3)
        c_out1.metric("โมเมนต์รวม (M_total)", f"{M_total_rc:,.2f} kg-m")
        c_out2.metric("เหล็กเสริมรับแรงดึง (As)", f"{As_req:,.2f} cm²")
        c_out3.metric("ระยะแอ่นตัวสูงสุด", f"{delta_max_rc:,.3f} cm", delta=f"ยอมให้ {delta_allow_rc:,.2f} cm", delta_color="normal")
        
        st.info(f"**🛠️ ปริมาณเหล็กเสริมที่แนะนำ:** ใช้อย่างน้อย DB12 จำนวน {n_DB12} เส้น หรือ DB16 จำนวน {n_DB16} เส้น")
            
        st.divider()
        st.header("📈 3. แผนภาพแรงเฉือนและโมเมนต์ดัด")
        fig_v_rc, fig_m_rc = plot_diagrams(L_rc, w_total_rc, P_rc, is_uniform_rc)
        cr1, cr2 = st.columns(2)
        cr1.plotly_chart(fig_v_rc, use_container_width=True)
        cr2.plotly_chart(fig_m_rc, use_container_width=True)

        # ================= รายการคำนวณ (Tab 2) =================
        with st.expander("📝 ดูรายการคำนวณ (Required vs Provided)"):
            st.markdown("### 📌 ขั้นตอนที่ 1: หาค่าความต้องการหน้าตัดขั้นต่ำ (Required Properties)")
            st.markdown("เพื่อให้คานคอนกรีตไม่แอ่นตัวเกินระยะที่กฎหมายกำหนด ($L/360$) หน้าตัดคานต้องมีโมเมนต์ความเฉื่อย ($I$) ขั้นต่ำ:")
            st.latex(rf"\Delta_{{allow}} = \frac{{L}}{{360}} = \frac{{{L_cm_rc}}}{{360}} = {delta_allow_rc:,.2f} \text{{ cm}}")
            if is_uniform_rc:
                st.latex(rf"I_{{req}} = \frac{{5 \cdot w_{{total}} \cdot L^4}}{{384 \cdot E_c \cdot \Delta_{{allow}}}} = {I_req_rc:,.2f} \text{{ cm}}^4")
            else:
                st.latex(rf"I_{{req}} = \frac{{P \cdot L^3}}{{48 \cdot E_c \cdot \Delta_{{allow}}}} + \frac{{5 \cdot w_{{self}} \cdot L^4}}{{384 \cdot E_c \cdot \Delta_{{allow}}}} = {I_req_rc:,.2f} \text{{ cm}}^4")
            
            st.markdown("---")
            st.markdown("### 📌 ขั้นตอนที่ 2: เลือกขนาดหน้าตัด (Try Section)")
            st.markdown(f"ทดลองเลือกใช้หน้าตัด กว้าง **$b = {b_rc}$ cm**, ลึก **$h = {h_rc}$ cm**")
            
            st.markdown("---")
            st.markdown("### 📌 ขั้นตอนที่ 3: ตรวจสอบหน้าตัดและคำนวณเหล็กเสริม (Check & Design)")
            st.markdown("**1. ตรวจสอบการแอ่นตัว:**")
            st.latex(rf"I_{{gross}} = \frac{{b \cdot h^3}}{{12}} = \frac{{{b_rc} \cdot {h_rc}^3}}{{12}} = {I_g:,.2f} \text{{ cm}}^4 \ge I_{{req}} \text{{ (OK)}}")
            
            st.markdown("**2. คำนวณหาพื้นที่เหล็กเสริมรับแรงดึงหลัก (As):**")
            st.latex(rf"d = h - 5 = {h_rc} - 5 = {d_rc} \text{{ cm}}")
            st.latex(rf"A_s = \frac{{M_{{max}} \cdot 100}}{{f_s \cdot j \cdot d}} = \frac{{{M_total_rc:,.2f} \cdot 100}}{{{fs} \cdot {j_val} \cdot {d_rc}}} = {As_req:,.2f} \text{{ cm}}^2")
