import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# T.-W. Lee, Aerospace Propulsion, Ch. 8
# Eq. 8.5: g0 = 9.8066 m/s^2
# Eq. 8.8: Ueq = Is*g0
# Eq. 8.11: Delta U = Ueq*ln(RM)
# Eq. 8.18: M0 = ML + Ms + Mp
# Eq. 8.19: Mb = ML + Ms
# Eq. 8.20: lambda = ML/(Mp+Ms)
# Eq. 8.21: epsilon = Ms/(Mp+Ms)
# Eq. 8.23: RM = (1+lambda)/(epsilon+lambda)
# Eq. 8.24: Delta U = sum[Ueq_i ln(RM_i)]
# Eq. 8.25: Delta U = n*Ueq*ln[(1+lambda)/(epsilon+lambda)] for similar stages

st.set_page_config(page_title="Rocket Delta-U Explorer", layout="wide")
G0 = 9.8066

def rm_from_ratios(lam, eps):
    return (1 + lam) / (eps + lam)

def ueq(Is):
    return Is * G0

st.title("🚀 Multi-Stage Rocket Velocity-Change Explorer")
st.caption("Equations follow T.-W. Lee, Aerospace Propulsion, Chapter 8.")

mode = st.radio(
    "Staging model",
    ["Similar Stages — Eq. (8.25)", "Individual Stages — Eq. (8.24)"],
    horizontal=True
)

tab_model, tab_contour, tab_eq = st.tabs([
    "Rocket Model",
    "Two-Variable Contour Study",
    "Equations & Calculation Steps"
])

with tab_model:
    if mode.startswith("Similar"):
        st.subheader("Similar stages — Eq. (8.25)")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            n = st.slider("Number of stages, n", 1, 5, 2, 1, key="sim_n")
        with c2:
            Is = st.slider("Specific impulse, Is (s)", 160, 385, 300, 1, key="sim_Is")
        with c3:
            lam_pct = st.slider("Payload ratio, λ (%)", 1.0, 15.0, 7.0, 0.1, key="sim_lam")
        with c4:
            eps_pct = st.slider("Structural mass coefficient, ε (%)", 18.0, 48.0, 25.0, 0.1, key="sim_eps")

        lam, eps = lam_pct/100, eps_pct/100
        RM = rm_from_ratios(lam, eps)
        Ueq = ueq(Is)
        du_stage = Ueq*np.log(RM)
        du_total = n*du_stage

        a,b,c,d = st.columns(4)
        a.metric("Mass ratio, RM", f"{RM:.4f}")
        b.metric("Equivalent exhaust velocity, Ueq", f"{Ueq:,.1f} m/s")
        c.metric("ΔU per stage", f"{du_stage/1000:.3f} km/s")
        d.metric("Total ΔU", f"{du_total/1000:.3f} km/s")

        st.markdown("#### Mass fractions implied by λ and ε")
        fractions = pd.DataFrame({
            "Mass category":["Payload","Structure","Propellant"],
            "Fraction of initial stage mass":[
                lam/(1+lam),
                eps/(1+lam),
                (1-eps)/(1+lam)
            ]
        })
        fractions["Percent"] = 100*fractions["Fraction of initial stage mass"]
        st.dataframe(fractions, use_container_width=True, hide_index=True)

        stage_df = pd.DataFrame({
            "Stage":np.arange(1,n+1),
            "Is (s)":[Is]*n,
            "Ueq (m/s)":[Ueq]*n,
            "λ":[lam]*n,
            "ε":[eps]*n,
            "RM":[RM]*n,
            "ΔUi (m/s)":[du_stage]*n
        })
        st.markdown("#### Stage-by-stage contribution")
        st.dataframe(stage_df, use_container_width=True, hide_index=True)

        fig = go.Figure(go.Bar(
            x=stage_df["Stage"], y=stage_df["ΔUi (m/s)"],
            text=[f"{v/1000:.2f} km/s" for v in stage_df["ΔUi (m/s)"]],
            textposition="outside"
        ))
        fig.update_layout(title="Velocity-change contribution of each similar stage",
                          xaxis_title="Stage", yaxis_title="ΔUi (m/s)", height=430)
        st.plotly_chart(fig, use_container_width=True)
        st.info("Eq. (8.25) gives equal stage contributions because similar stages use the same Ueq, λ, ε, and RM.")

    else:
        st.subheader("Individual stages — Eq. (8.24)")
        st.write("Stage 1 is the bottom/first-burning stage. Each lower stage carries the complete initial mass of the stage above it.")

        n = st.slider("Number of stages", 1, 5, 2, 1, key="ind_n")
        final_payload = st.number_input("Final payload mass, ML (kg)", min_value=1.0, value=1000.0, step=50.0)

        defaults_mp = [9000.,2200.,650.,180.,60.]
        defaults_ms = [1800.,500.,160.,60.,25.]
        defaults_is = [280.,310.,330.,350.,365.]

        inputs = []
        st.markdown("#### Enter stage properties")
        for i in range(1,n+1):
            st.markdown(f"**Stage {i}**")
            x,y,z = st.columns(3)
            with x:
                Mp = st.number_input(f"Stage {i} propellant mass, Mp (kg)", min_value=0.1,
                                     value=defaults_mp[i-1], step=50.0, key=f"Mp{i}")
            with y:
                Ms = st.number_input(f"Stage {i} structural mass, Ms (kg)", min_value=0.1,
                                     value=defaults_ms[i-1], step=10.0, key=f"Ms{i}")
            with z:
                Is_i = st.number_input(f"Stage {i} specific impulse, Is (s)", min_value=1.0,
                                       value=defaults_is[i-1], step=1.0, key=f"Is{i}")
            inputs.append((i,Mp,Ms,Is_i))

        carried = final_payload
        rows = []
        for i,Mp,Ms,Is_i in reversed(inputs):
            ML = carried
            M0 = ML + Ms + Mp
            Mb = ML + Ms
            RM = M0/Mb
            Ueq = ueq(Is_i)
            dUi = Ueq*np.log(RM)
            rows.append({
                "Stage":i, "ML carried (kg)":ML, "Ms (kg)":Ms, "Mp (kg)":Mp,
                "M0 (kg)":M0, "Mb (kg)":Mb, "Is (s)":Is_i, "Ueq (m/s)":Ueq,
                "λ":ML/(Mp+Ms), "ε":Ms/(Mp+Ms), "RM":RM, "ΔUi (m/s)":dUi
            })
            carried = M0

        df = pd.DataFrame(list(reversed(rows)))
        total_du = df["ΔUi (m/s)"].sum()
        a,b,c = st.columns(3)
        a.metric("Lift-off mass, M0,1", f"{df.iloc[0]['M0 (kg)']:,.1f} kg")
        b.metric("Final payload", f"{final_payload:,.1f} kg")
        c.metric("Total ΔU", f"{total_du/1000:.3f} km/s")

        st.markdown("#### Calculated stage properties")
        st.dataframe(df, use_container_width=True, hide_index=True)

        fig = go.Figure(go.Bar(
            x=df["Stage"], y=df["ΔUi (m/s)"],
            text=[f"{v/1000:.2f} km/s" for v in df["ΔUi (m/s)"]],
            textposition="outside"
        ))
        fig.update_layout(title="Velocity-change contribution of each individual stage",
                          xaxis_title="Stage", yaxis_title="ΔUi (m/s)", height=430)
        st.plotly_chart(fig, use_container_width=True)

        mass_df = df[["Stage","M0 (kg)","Mb (kg)","ML carried (kg)"]].set_index("Stage")
        st.markdown("#### Mass change through staging")
        st.line_chart(mass_df, use_container_width=True)

with tab_contour:
    st.subheader("Two-variable study — similar-stage Eq. (8.25)")
    vars_ = ["Number of stages, n","Specific impulse, Is (s)","Payload ratio, λ (%)","Structural mass coefficient, ε (%)"]
    xv = st.selectbox("X-axis variable", vars_, index=1)
    yv = st.selectbox("Y-axis variable", [v for v in vars_ if v != xv], index=1)

    c1,c2,c3,c4 = st.columns(4)
    with c1: fn = st.slider("Fixed n",1,5,2,1,key="fn")
    with c2: fIs = st.slider("Fixed Is (s)",160,385,300,1,key="fIs")
    with c3: flam = st.slider("Fixed λ (%)",1.0,15.0,7.0,0.1,key="flam")
    with c4: feps = st.slider("Fixed ε (%)",18.0,48.0,25.0,0.1,key="feps")

    def axis(v):
        if v=="Number of stages, n": return np.arange(1,6,dtype=float)
        if v=="Specific impulse, Is (s)": return np.linspace(160,385,90)
        if v=="Payload ratio, λ (%)": return np.linspace(1,15,90)
        return np.linspace(18,48,90)

    x,y = axis(xv),axis(yv)
    X,Y = np.meshgrid(x,y)
    N=np.full_like(X,float(fn)); IS=np.full_like(X,float(fIs))
    L=np.full_like(X,float(flam)); E=np.full_like(X,float(feps))
    for v,A in [(xv,X),(yv,Y)]:
        if v=="Number of stages, n": N=A
        elif v=="Specific impulse, Is (s)": IS=A
        elif v=="Payload ratio, λ (%)": L=A
        else: E=A
    RM=(1+L/100)/(E/100+L/100)
    Z=N*(IS*G0)*np.log(RM)/1000

    fig=go.Figure(go.Contour(x=x,y=y,z=Z,contours=dict(showlabels=True),colorbar=dict(title="ΔU (km/s)")))
    fig.update_layout(title=f"Total ΔU vs. {xv} and {yv}",xaxis_title=xv,yaxis_title=yv,height=620)
    st.plotly_chart(fig,use_container_width=True)

    mn=np.unravel_index(np.argmin(Z),Z.shape); mx=np.unravel_index(np.argmax(Z),Z.shape)
    st.dataframe(pd.DataFrame({
        "Point":["Minimum","Maximum"],
        "ΔU (km/s)":[Z[mn],Z[mx]],
        xv:[X[mn],X[mx]], yv:[Y[mn],Y[mx]]
    }),use_container_width=True,hide_index=True)

with tab_eq:
    st.subheader("Equations and calculation walkthrough")
    st.write("These are the Chapter 8 equations used in the app, followed by live substitution of the current inputs.")

    st.markdown("### Eqs. (8.18)–(8.21): masses and ratios")
    st.latex(r"M_0=M_L+M_s+M_p")
    st.latex(r"M_b=M_L+M_s")
    st.latex(r"\lambda=\frac{M_L}{M_p+M_s}")
    st.latex(r"\epsilon=\frac{M_s}{M_p+M_s}")

    st.markdown("### Eq. (8.23): back-substitution")
    st.markdown(r"""
Let (S=M_p+M_s). Then (M_L=lambda S) and (M_s=epsilon S).

[
M_0=M_L+M_s+M_p=lambda S+S=(1+lambda)S
]

[
M_b=M_L+M_s=lambda S+epsilon S=(lambda+epsilon)S
]

Therefore,

[
R_M=rac{M_0}{M_b}
=rac{(1+lambda)S}{(epsilon+lambda)S}
=oxed{rac{1+lambda}{epsilon+lambda}}
]
""")

    st.markdown("### Eqs. (8.5), (8.8), and (8.11)")
    st.latex(r"g_0=9.8066\ \mathrm{m/s^2}")
    st.latex(r"U_{eq}=I_sg_0")
    st.latex(r"\Delta U=U_{eq}\ln R_M=g_0I_s\ln R_M")

    st.markdown("### Eq. (8.24): general multi-stage form")
    st.latex(r"\Delta U=\sum_{i=1}^{n}U_{eq,i}\ln R_{M,i}")

    st.markdown("### Eq. (8.25): similar-stage form")
    st.latex(r"\Delta U=nU_{eq}\ln\left(\frac{1+\lambda}{\epsilon+\lambda}\right)")

    st.divider()
    if mode.startswith("Similar"):
        st.markdown("## Current similar-stage calculation")
        n=st.session_state.get("sim_n",2); Is=st.session_state.get("sim_Is",300)
        lam=st.session_state.get("sim_lam",7.0)/100; eps=st.session_state.get("sim_eps",25.0)/100
        RM=rm_from_ratios(lam,eps); Ueq=ueq(Is); dui=Ueq*np.log(RM); total=n*dui
        st.latex(rf"R_M=\frac{{1+{lam:.4f}}}{{{eps:.4f}+{lam:.4f}}}={RM:.4f}")
        st.latex(rf"U_{{eq}}=({Is})(9.8066)={Ueq:.2f}\ \mathrm{{m/s}}")
        st.latex(rf"\Delta U_i=({Ueq:.2f})\ln({RM:.4f})={dui:.2f}\ \mathrm{{m/s}}")
        st.latex(rf"\Delta U_{{total}}=({n})({dui:.2f})={total:.2f}\ \mathrm{{m/s}}")
        st.markdown("The propellant fraction within (M_p+M_s) follows directly from Eq. (8.21):")
        st.latex(rf"\frac{{M_p}}{{M_p+M_s}}=1-\epsilon=1-{eps:.4f}={1-eps:.4f}")
    else:
        st.markdown("## Current individual-stage calculation")
        n=st.session_state.get("ind_n",2)
        final_payload=float(final_payload)
        vals=[]
        for i in range(1,n+1):
            vals.append((i,float(st.session_state[f"Mp{i}"]),float(st.session_state[f"Ms{i}"]),float(st.session_state[f"Is{i}"])))
        carried=final_payload; calc=[]
        for i,Mp,Ms,Is_i in reversed(vals):
            ML=carried; M0=ML+Ms+Mp; Mb=ML+Ms; RM=M0/Mb; U=ueq(Is_i); dU=U*np.log(RM)
            calc.append((i,ML,Mp,Ms,M0,Mb,Is_i,U,RM,dU)); carried=M0
        calc=list(reversed(calc))
        for i,ML,Mp,Ms,M0,Mb,Is_i,U,RM,dU in calc:
            with st.expander(f"Stage {i} calculation", expanded=(i==1)):
                st.latex(rf"M_{{0,{i}}}={ML:.2f}+{Ms:.2f}+{Mp:.2f}={M0:.2f}\ \mathrm{{kg}}")
                st.latex(rf"M_{{b,{i}}}={ML:.2f}+{Ms:.2f}={Mb:.2f}\ \mathrm{{kg}}")
                st.latex(rf"R_{{M,{i}}}=\frac{{{M0:.2f}}}{{{Mb:.2f}}}={RM:.4f}")
                st.latex(rf"U_{{eq,{i}}}=({Is_i:.1f})(9.8066)={U:.2f}\ \mathrm{{m/s}}")
                st.latex(rf"\Delta U_{i}=({U:.2f})\ln({RM:.4f})={dU:.2f}\ \mathrm{{m/s}}")
        total=sum(r[-1] for r in calc)
        st.latex(rf"\Delta U_{{total}}={total:.2f}\ \mathrm{{m/s}}")

st.divider()
st.caption("Ideal Chapter 8 staging equations only; gravity, drag, steering, and trajectory losses are not added to Eqs. (8.24) or (8.25).")
