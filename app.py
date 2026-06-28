import streamlit as st
import math
import numpy as np
import plotly.graph_objects as go

# ==========================================
# ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Beam Design Pro", page_icon="🏗️", layout="wide")

st.title("🏗️ โปรแกรมออกแบบขนาดคานเบื้องต้น (Pro Version)")
st.markdown("ระบบวิเคราะห์หน้าตัดคาน รองรับ Wide Flange/H-Beam (เจาะลึก) และ RC T-Beam (คานรูปตัวที)")
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
        
        # ตัวแปรเสริมสำหรับ Manual Mode
        tw_manual, tf_manual = None, None 

        if "Auto" in design_mode_homo:
            ratio = st.number_input("สัดส่วน ความลึก/ความกว้าง (h/b)", min_value=1.0, value=2.0, step=0.5, key="ratio_homo")
            b_manual_homo, h_manual_homo = 0, 0
            st.caption("💡 ระบบจะหาขนาดเชิงทฤษฎีที่เล็กที่สุดให้ โดยจำลองความหนา $t_f, t_w$ ตามสัดส่วนมาตรฐาน")
        else:
            if section_shape == "หน้าตัดไวด์แฟลงก์ / เอชบีม (Wide Flange / H-Beam)":
                st.markdown("**ป้อนขนาดหน้าตัดจริง (สามารถเทียบจากตารางเหล็กได้)**")
                c_sec1, c_sec2 = st.columns(2)
                h_manual_homo = c_sec1.number_input("ความลึกคาน H (cm)", min_value=5.0, value=20.0, step=1.0)
                b_manual_homo = c_sec2.number_input("ความกว้างปีก B (cm)", min_value=5.0, value=10.0, step=1.0)
                c_sec3, c_sec4 = st.columns(2)
                tw_manual = c_sec3.number_input("ความหนาเอว tw (mm)", min_value=1.0, value=5.5, step=0.5) / 10.0 # แปลงเป็น cm
                tf_manual = c_sec4.number_input("ความหนาปีก tf (mm)", min_value=1.0, value=8.0, step=0.5) / 10.0 # แปลงเป็น cm
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
        
        # ฟังก์ชันคำนวณหน้าตัดรองรับการระบุ tw, tf แบบ Manual
        def calc_section(b, h, tw_val=None, tf_val=None):
            if section_shape == "หน้าตัดสี่เหลี่ยมตัน (Solid Rectangle)":
                w_s = (b / 100) * (h / 100) * density
                I_p = (b * h**3) / 12
                S_p = (b * h**2) / 6
                out_tw, out_tf = 0, 0
            else:
                # ถ้าไม่ระบุค่ามา (Auto mode) ให้ประมาณการ
                out_tf = tf_val if tf_val is not None else 0.06 * h
                out_tw = tw_val if tw_val is not None else 0.04 * h
                
                # เช็คป้องกันค่าหนาเกินไปจนผิดปกติ
                if 2 * out_tf >= h: out_tf = h * 0.4
                if out_tw >= b: out_tw = b * 0.5
                
                area_cm2 = (2 * b * out_tf) + ((h - 2 * out_tf) * out_tw)
                w_s = (area_cm2 / 10000) * density
                
                # คำนวณ I อย่างแม่นยำ (Moment of Inertia)
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
        
        # Check Shear for Wide Flange (ตรวจแรงเฉือนเอวคาน)
        fv_actual = V_max_homo / (h_final * tw) if tw > 0 else 0
        shear_safe = True if (tw == 0 or fv_actual <= tau_allow) else False
        if not shear_safe: is_safe = False

        if is_uniform_homo:
            delta_max = (5 * (w_total_actual / 100) * L_cm**4) / (384 * E_val * I_prov)
        else:
            delta_max = ((P_homo * L_cm**3) / (48 * E_val * I_prov)) + ((5 * (w_self_actual / 100) * L_cm**4) / (384 * E_val * I_prov))

        st.divider()
        st.header("📊 2. สรุปผลการประเมินหน้าตัดขั้นสุดท้าย")
        
        if not is_safe and "Manual" in design_mode_homo:
            st.error(f"❌ **ขนาดหน้าตัด H-{h_final:.0f}x{b_final:.0f} ที่ระบุไม่ปลอดภัย!** อาจเกิดจากการรับแรงดัด (S ไม่พอ), การแอ่นตัวเกิน, หรือความหนาเอว (tw) ไม่เพียงพอรับแรงเฉือน")
        elif is_safe:
            st.success(f"### 📐 ขนาดที่ใช้: กว้าง {b_final:.0f} ซม. × ลึก {h_final:.0f} ซม.")
            if "Wide" in section_shape:
                st.info(f"**รายละเอียดสัดส่วน Wide Flange:** H-{h_final*10:.0f}x{b_final*10:.0f}x{tw*10:.1f}x{tf*10:.1f} mm. | พื้นที่หน้าตัด (A) = {((2 * b_final * tf) + ((h_final - 2 * tf) * tw)):.2f} cm²")
        
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

        with st.expander("📝 ดูรายการคำนวณแบบละเอียด"):
            st.markdown(r"**1. ตรวจสอบพิกัดต้านทานการดัด (Section Modulus Check):**")
            pass_S = "OK" if S_prov >= S_req_final else "NG (เพิ่ม H หรือ tf)"
            st.latex(rf"S_{{prov}} ({S_prov:,.2f} \text{{ cm}}^3) \ge S_{{req}} ({S_req_final:,.2f} \text{{ cm}}^3) \implies \text{{{pass_S}}}")
            
            st.markdown(r"**2. ตรวจสอบพิกัดควบคุมการแอ่นตัว (Moment of Inertia Check):**")
            pass_I = "OK" if I_prov >= I_req_final else "NG (เพิ่ม H)"
            st.latex(rf"I_{{prov}} ({I_prov:,.2f} \text{{ cm}}^4) \ge I_{{req}} ({I_req_final:,.2f} \text{{ cm}}^4) \implies \text{{{pass_I}}}")
            
            if "Wide" in section_shape:
                st.markdown(r"**3. ตรวจสอบหน่วยแรงเฉือนในเอวคาน (Web Shear Check):**")
                st.latex(rf"f_v = \frac{{V_{{max}}}}{{h \cdot t_w}} = \frac{{{V_max_homo:,.2f}}}{{{h_final:.2f} \cdot {tw:.2f}}} = {fv_actual:,.2f} \text{{ ksc}}")
                pass_V = "OK" if fv_actual <= tau_allow else "NG (เพิ่มความหนาเอว tw)"
                st.latex(rf"f_v \le F_v ({tau_allow:,.2f} \text{{ ksc}}) \implies \text{{{pass_V}}}")
# ==========================================
# TAB 2: คอนกรีตเสริมเหล็ก (RC Beam)
# ==========================================
with tab2:
    st.header("📝 1. ป้อนข้อมูลการออกแบบ (คาน RC)")
    design_mode_rc = st.radio("โหมดการออกแบบ (RC Beam)", ["🔍 คำนวณขนาดอัตโนมัติ (Auto-sizing)", "✍️ กำหนดขนาดเอง (Manual)"], horizontal=True, key="mode_rc")
    
    st.markdown("---")
    rc_shape = st.selectbox("📌 รูปแบบหน้าตัดคานคอนกรีต", ["คานสี่เหลี่ยมผืนผ้า (Rectangular Beam)", "คานรูปตัวที (T-Beam)"], key="rc_shape")
    
    if rc_shape == "คานรูปตัวที (T-Beam)":
        st.caption("💡 คานตัวที: ปีกคาน (พื้น) ช่วยรับแรงอัด ทำให้ประหยัดเหล็กและแข็งแรงขึ้น")
        col_t1, col_t2 = st.columns(2)
        bf_rc = col_t1.number_input("ความกว้างปีกคาน/ความกว้างพื้นที่มีผล (bf) (cm)", min_value=10.0, value=100.0, step=10.0)
        hf_rc = col_t2.number_input("ความหนาปีกคาน/ความหนาพื้น (hf) (cm)", min_value=5.0, value=10.0, step=1.0)
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
                # น้ำหนักตัวเองคิดเฉพาะส่วนเอวคานที่ย้อยลงมาใต้พื้น (ลดความซ้ำซ้อนของนน.พื้น)
                w_self = (bw / 100) * ((h - hf_rc) / 100) * 2400 if h > hf_rc else 0
                # คำนวณ I_gross ของหน้าตัดตัวที
                A1 = bf_rc * hf_rc
                A2 = bw * (h - hf_rc) if h > hf_rc else 0
                if A1 + A2 > 0:
                    y_bar = (A1 * (hf_rc / 2) + A2 * (hf_rc + (h - hf_rc)/2)) / (A1 + A2)
                    Ig_1 = (bf_rc * hf_rc**3)/12 + A1 * (y_bar - hf_rc/2)**2
                    Ig_2 = (bw * (h - hf_rc)**3)/12 + A2 * (hf_rc + (h - hf_rc)/2 - y_bar)**2 if h > hf_rc else 0
                    Ig = Ig_1 + Ig_2
                else:
                    Ig = 1
                Mc = (R_wsd * bf_rc * d**2) / 100  # วิเคราะห์หน้าตัดเสมือนกว้าง bf
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
            # คำนวณปริมาณเหล็กเสริม
            As_req = (M_total_rc * 100) / (fs * j_val * d_rc) if d_rc > 0 else 0
            As_min = (14.0 / fy) * bw_rc * d_rc
            As_final = max(As_req, As_min)
            n_DB12 = math.ceil(As_final / 1.13)
            n_DB16 = math.ceil(As_final / 2.01)
            
            # การออกแบบแรงเฉือน (ใช้แค่ความกว้าง Web bw ในการรับแรงเฉือนเสมอ แม้จะเป็น T-Beam)
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
                    st.success(f"### 📐 หน้าตัดที่ใช้งาน (T-Beam): เอวคานกว้าง $b_w$ = {bw_rc:.0f} ซม., ลึกรวม $h$ = {h_rc:.0f} ซม.")
                    st.info(f"**ปีกคาน (Flange):** กว้าง {bf_rc} ซม. หนา {hf_rc} ซม. (ช่วยเพิ่มสติฟเนส $I_{{gross}}$ เป็น {I_g:,.2f} cm$^4$)")
                else:
                    st.success(f"### 📐 หน้าตัดคาน (Rectangular): กว้าง {bw_rc:.0f} ซม. × ลึก {h_rc:.0f} ซม.")
            
            c_out1, c_out2, c_out3 = st.columns(3)
            c_out1.metric("โมเมนต์ดัดรวม (M_total)", f"{M_total_rc:,.2f} kg-m")
            c_out2.metric("เหล็กแกนดึงที่ต้องการ (As)", f"{As_final:,.2f} cm²", delta=f"เหล็กขั้นต่ำ {As_min:.2f} cm²")
            c_out3.metric("หน่วยแรงเฉือน (v_v)", f"{v_v:,.2f} ksc", delta=f"คอนกรีตรับได้ {v_c:,.2f} ksc", delta_color="normal" if v_v <= v_c else "inverse")
            
            if is_rc_safe or "Manual" in design_mode_rc:
                st.info(f"**🛠️ เหล็กเสริมหลัก:** แนะนำใช้ DB12 จำนวน {max(2, n_DB12)} เส้น หรือ DB16 จำนวน {max(2, n_DB16)} เส้น")
                if s_spacing_final > 0:
                    st.warning(f"**🛡️ เหล็กปลอกรับแรงเฉือน:** {stirrup_text} ใช้ **{stirrup_bar} @ {s_spacing_final} ซม.**")

            with st.expander("📝 ดูรายการคำนวณ RC เจาะลึก"):
                st.markdown(r"**1. ตรวจสอบกำลังคอนกรีตรับแรงอัด ($M_c = R b d^2$):**")
                pass_Mc = "OK" if M_concrete_capacity >= M_total_rc else "NG"
                b_calc = bf_rc if rc_shape == "คานรูปตัวที (T-Beam)" else bw_rc
                st.latex(rf"M_c = \frac{{{R_wsd:.2f} \cdot {b_calc:.0f} \cdot {d_rc}^2}}{{100}} = {M_concrete_capacity:,.2f} \text{{ kg-m}} \ge {M_total_rc:,.2f} \implies \text{{{pass_Mc}}}")
                
                st.markdown(r"**2. ตรวจสอบหน่วยแรงเฉือน (Shear Check):**")
                st.markdown("⚠️ *การรับแรงเฉือนจะคิดเฉพาะความกว้างเอวคาน ($b_w$) เท่านั้น ไม่รวมปีก*")
                st.latex(rf"v_v = \frac{{V_{{max}}}}{{b_w \cdot d}} = \frac{{{V_max_rc:,.2f}}}{{{bw_rc:.0f} \cdot {d_rc}}} = {v_v:.2f} \text{{ ksc}}")
