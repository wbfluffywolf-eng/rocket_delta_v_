import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from itertools import product

# T.-W. Lee, Aerospace Propulsion
# Ch. 8: Eqs. 8.5, 8.8, 8.11, 8.18-8.25
# Ch. 10: Table 10.2 launch-vehicle propellant/engine examples

st.set_page_config(page_title="Rocket Delta-U Explorer", layout="wide")
G0 = 9.8066

BOOK_PROPULSION = {
    "Atlas YLR89-NA7 — LOX/RP-1": {"propellant":"LOX/RP-1","vehicle":"Atlas/Centaur","engine":"YLR89-NA7","sea":259.0,"vac":292.0},
    "Atlas YLR105-NA7 — LOX/RP-1": {"propellant":"LOX/RP-1","vehicle":"Atlas/Centaur","engine":"YLR105-NA7","sea":220.0,"vac":309.0},
    "Centaur RL-10A-3-3 — LOX/LH2": {"propellant":"LOX/LH2","vehicle":"Atlas/Centaur","engine":"RL-10A-3-3","sea":None,"vac":444.0},
    "Titan II LR-87-AJ-5 — NTO/Aerozine 50": {"propellant":"NTO/Aerozine 50","vehicle":"Titan II","engine":"LR-87-AJ-5","sea":259.0,"vac":285.0},
    "Titan II LR-91-AJ-5 — NTO/Aerozine 50": {"propellant":"NTO/Aerozine 50","vehicle":"Titan II","engine":"LR-91-AJ-5","sea":None,"vac":312.0},
    "Saturn V F-1 — LOX/RP-1": {"propellant":"LOX/RP-1","vehicle":"Saturn V","engine":"F-1","sea":265.0,"vac":304.0},
    "Saturn V J-2 — LOX/LH2": {"propellant":"LOX/LH2","vehicle":"Saturn V","engine":"J-2","sea":None,"vac":424.0},
    "Space Shuttle SRB — PBAN solid": {"propellant":"PBAN solid","vehicle":"Space Shuttle","engine":"SRB","sea":242.0,"vac":268.0},
    "Space Shuttle SSME — LOX/LH2": {"propellant":"LOX/LH2","vehicle":"Space Shuttle","engine":"SSME","sea":363.0,"vac":453.0},
    "Space Shuttle OMS — NTO/MMH": {"propellant":"NTO/MMH","vehicle":"Space Shuttle","engine":"OMS","sea":None,"vac":313.0},
    "Space Shuttle RCS — NTO/MMH": {"propellant":"NTO/MMH","vehicle":"Space Shuttle","engine":"RCS","sea":None,"vac":280.0},
    "Delta II Castor 4A — HTPB solid": {"propellant":"HTPB solid","vehicle":"Delta II","engine":"Castor 4A","sea":238.0,"vac":266.0},
    "Delta II RS-27 — LOX/RP-1": {"propellant":"LOX/RP-1","vehicle":"Delta II","engine":"RS-27","sea":264.0,"vac":295.0},
    "Delta II AJ10-118K — NTO/Aerozine 50": {"propellant":"NTO/Aerozine 50","vehicle":"Delta II","engine":"AJ10-118K","sea":None,"vac":320.0},
}

def ueq(Is):
    return Is * G0

def rm_from_ratios(lam, eps):
    return (1 + lam) / (eps + lam)

def isp_for(label, environment):
    d = BOOK_PROPULSION[label]
    return d["sea"] if environment == "Sea level" else d["vac"]

def build_individual_rows(stage_inputs, final_payload):
    carried = final_payload
    rows = []
    for s in reversed(stage_inputs):
        ML = carried
        M0 = ML + s["Ms"] + s["Mp"]
        Mb = ML + s["Ms"]
        RM = M0 / Mb
        Ueq = ueq(s["Is"])
        dU = Ueq * np.log(RM)
        rows.append({
            "Stage": s["stage"],
            "Propellant": s["propellant"],
            "Book example": s["example"],
            "Is condition": s["environment"],
            "ML carried (kg)": ML,
            "Ms (kg)": s["Ms"],
            "Mp (kg)": s["Mp"],
            "M0 (kg)": M0,
            "Mb (kg)": Mb,
            "Is (s)": s["Is"],
            "Ueq (m/s)": Ueq,
            "lambda": ML / (s["Mp"] + s["Ms"]),
            "epsilon": s["Ms"] / (s["Mp"] + s["Ms"]),
            "RM": RM,
            "Delta Ui (m/s)": dU,
        })
        carried = M0
    return pd.DataFrame(list(reversed(rows)))

st.title("🚀 Multi-Stage Rocket Velocity-Change Explorer")
st.caption("Book equations: T.-W. Lee, Aerospace Propulsion. Propellant examples: Table 10.2.")

mode = st.radio(
    "Staging model",
    ["Similar Stages — Eq. (8.25)", "Individual Stages — Eq. (8.24)"],
    horizontal=True
)

tab_model, tab_contour, tab_prop, tab_eq = st.tabs([
    "Rocket Model",
    "Two-Variable Contour Study",
    "Propellant Comparison",
    "Equations & Calculation Steps",
])

with tab_model:
    if mode.startswith("Similar"):
        st.subheader("Similar stages — Eq. (8.25)")
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            n = st.slider("Number of stages, n", 1, 5, 3, 1, key="sim_n")
        with c2:
            Is = st.slider("Specific impulse, Is (s)", 160, 385, 300, 1, key="sim_Is")
        with c3:
            lam_pct = st.slider("Payload ratio, lambda (%)", 1.0, 15.0, 7.0, 0.1, key="sim_lam")
        with c4:
            eps_pct = st.slider("Structural mass coefficient, epsilon (%)", 18.0, 48.0, 25.0, 0.1, key="sim_eps")

        lam = lam_pct/100
        eps = eps_pct/100
        RM = rm_from_ratios(lam,eps)
        Ueq = ueq(Is)
        dUstage = Ueq*np.log(RM)
        total = n*dUstage

        a,b,c,d = st.columns(4)
        a.metric("RM", f"{RM:.4f}")
        b.metric("Ueq", f"{Ueq:,.1f} m/s")
        c.metric("Delta U per stage", f"{dUstage/1000:.3f} km/s")
        d.metric("Total Delta U", f"{total/1000:.3f} km/s")

        fractions = pd.DataFrame({
            "Mass category":["Payload","Structure","Propellant"],
            "Fraction of initial mass":[lam/(1+lam), eps/(1+lam), (1-eps)/(1+lam)]
        })
        fractions["Percent"] = 100*fractions["Fraction of initial mass"]
        st.markdown("#### Mass fractions implied by lambda and epsilon")
        st.dataframe(fractions,use_container_width=True,hide_index=True)

        stage_df = pd.DataFrame({
            "Stage":np.arange(1,n+1),
            "Is (s)":[Is]*n,
            "Ueq (m/s)":[Ueq]*n,
            "RM":[RM]*n,
            "Delta Ui (m/s)":[dUstage]*n
        })
        fig = go.Figure(go.Bar(
            x=stage_df["Stage"], y=stage_df["Delta Ui (m/s)"],
            text=[f"{v/1000:.2f} km/s" for v in stage_df["Delta Ui (m/s)"]],
            textposition="outside"
        ))
        fig.update_layout(title="Velocity-change contribution of each similar stage",
                          xaxis_title="Stage",yaxis_title="Delta Ui (m/s)",height=430)
        st.plotly_chart(fig,use_container_width=True)
        st.info("Equal bars are expected in Eq. (8.25) because similar stages use the same Ueq, lambda, epsilon, and RM.")

    else:
        st.subheader("Individual stages — Eq. (8.24)")
        n = st.slider("Number of stages",1,5,3,1,key="ind_n")
        final_payload = st.number_input("Final payload mass, ML (kg)",min_value=1.0,value=1000.0,step=50.0,key="final_payload")

        default_mp=[9000.,2200.,650.,180.,60.]
        default_ms=[1800.,500.,160.,60.,25.]
        defaults=[
            "Saturn V F-1 — LOX/RP-1",
            "Saturn V J-2 — LOX/LH2",
            "Centaur RL-10A-3-3 — LOX/LH2",
            "Space Shuttle OMS — NTO/MMH",
            "Delta II AJ10-118K — NTO/Aerozine 50",
        ]
        labels=list(BOOK_PROPULSION.keys())
        inputs=[]

        for i in range(1,n+1):
            st.markdown(f"**Stage {i}**")
            a,b,c,d = st.columns(4)
            with a:
                Mp=st.number_input(f"Stage {i} propellant mass, Mp (kg)",min_value=0.1,value=default_mp[i-1],step=50.0,key=f"Mp{i}")
            with b:
                Ms=st.number_input(f"Stage {i} structural mass, Ms (kg)",min_value=0.1,value=default_ms[i-1],step=10.0,key=f"Ms{i}")
            with c:
                choice=st.selectbox(f"Stage {i} propellant / engine",labels,index=labels.index(defaults[i-1]),key=f"prop{i}")
            data=BOOK_PROPULSION[choice]
            envs=[]
            if data["sea"] is not None: envs.append("Sea level")
            if data["vac"] is not None: envs.append("Vacuum")
            default_env="Sea level" if i==1 and "Sea level" in envs else envs[-1]
            with d:
                env=st.selectbox(f"Stage {i} Is condition",envs,index=envs.index(default_env),key=f"env{i}")
            Is_i=isp_for(choice,env)
            st.caption(f"{data['propellant']} • {data['vehicle']} {data['engine']} • Is = {Is_i:.0f} s ({env.lower()})")
            inputs.append({"stage":i,"Mp":Mp,"Ms":Ms,"Is":Is_i,"propellant":data["propellant"],"example":choice,"environment":env})

        df=build_individual_rows(inputs,final_payload)
        total=df["Delta Ui (m/s)"].sum()
        a,b,c=st.columns(3)
        a.metric("Lift-off mass",f"{df.iloc[0]['M0 (kg)']:,.1f} kg")
        b.metric("Final payload",f"{final_payload:,.1f} kg")
        c.metric("Total Delta U",f"{total/1000:.3f} km/s")
        st.dataframe(df,use_container_width=True,hide_index=True)

        fig=go.Figure(go.Bar(
            x=df["Stage"],y=df["Delta Ui (m/s)"],
            text=[f"{v/1000:.2f} km/s" for v in df["Delta Ui (m/s)"]],
            textposition="outside"
        ))
        fig.update_layout(title="Velocity-change contribution by individual stage",
                          xaxis_title="Stage",yaxis_title="Delta Ui (m/s)",height=430)
        st.plotly_chart(fig,use_container_width=True)

with tab_contour:
    st.subheader("Two-variable study — Eq. (8.25)")
    variables=["Number of stages, n","Specific impulse, Is (s)","Payload ratio, lambda (%)","Structural mass coefficient, epsilon (%)"]
    xv=st.selectbox("X-axis variable",variables,index=1)
    yv=st.selectbox("Y-axis variable",[v for v in variables if v!=xv],index=1)
    c1,c2,c3,c4=st.columns(4)
    with c1: fn=st.slider("Fixed n",1,5,3,1,key="fn")
    with c2: fIs=st.slider("Fixed Is (s)",160,385,300,1,key="fIs")
    with c3: flam=st.slider("Fixed lambda (%)",1.0,15.0,7.0,0.1,key="flam")
    with c4: feps=st.slider("Fixed epsilon (%)",18.0,48.0,25.0,0.1,key="feps")

    def axis(v):
        if v=="Number of stages, n": return np.arange(1,6,dtype=float)
        if v=="Specific impulse, Is (s)": return np.linspace(160,385,90)
        if v=="Payload ratio, lambda (%)": return np.linspace(1,15,90)
        return np.linspace(18,48,90)

    x,y=axis(xv),axis(yv)
    X,Y=np.meshgrid(x,y)
    N=np.full_like(X,float(fn)); IS=np.full_like(X,float(fIs))
    L=np.full_like(X,float(flam)); E=np.full_like(X,float(feps))
    for v,A in [(xv,X),(yv,Y)]:
        if v=="Number of stages, n": N=A
        elif v=="Specific impulse, Is (s)": IS=A
        elif v=="Payload ratio, lambda (%)": L=A
        else: E=A
    RM=(1+L/100)/(E/100+L/100)
    Z=N*(IS*G0)*np.log(RM)/1000
    fig=go.Figure(go.Contour(x=x,y=y,z=Z,contours=dict(showlabels=True),colorbar=dict(title="Delta U (km/s)")))
    fig.update_layout(title=f"Total Delta U vs. {xv} and {yv}",xaxis_title=xv,yaxis_title=yv,height=620)
    st.plotly_chart(fig,use_container_width=True)

with tab_prop:
    st.subheader("Book propellant / engine comparison")
    st.write("Table 10.2 gives specific impulse for actual launch-vehicle engine/propellant examples. Is is not a universal property of the propellant alone; engine/nozzle design and operating condition matter.")

    picks=st.multiselect(
        "Select examples to compare",
        list(BOOK_PROPULSION.keys()),
        default=["Saturn V F-1 — LOX/RP-1","Saturn V J-2 — LOX/LH2","Titan II LR-87-AJ-5 — NTO/Aerozine 50","Delta II Castor 4A — HTPB solid"]
    )
    rows=[]
    for label in picks:
        d=BOOK_PROPULSION[label]
        rows.append({
            "Book example":label,
            "Propellant":d["propellant"],
            "Sea-level Is (s)":d["sea"],
            "Vacuum Is (s)":d["vac"]
        })
    if rows:
        comp=pd.DataFrame(rows)
        st.dataframe(comp,use_container_width=True,hide_index=True)
        long=[]
        for r in rows:
            if r["Sea-level Is (s)"] is not None: long.append({"Example":r["Book example"],"Condition":"Sea level","Is":r["Sea-level Is (s)"]})
            if r["Vacuum Is (s)"] is not None: long.append({"Example":r["Book example"],"Condition":"Vacuum","Is":r["Vacuum Is (s)"]})
        long=pd.DataFrame(long)
        fig=go.Figure()
        for cond in long["Condition"].unique():
            q=long[long["Condition"]==cond]
            fig.add_trace(go.Bar(name=cond,x=q["Example"],y=q["Is"]))
        fig.update_layout(barmode="group",title="Book-listed specific impulse comparison",yaxis_title="Is (s)",height=520)
        st.plotly_chart(fig,use_container_width=True)

    st.divider()
    st.subheader("Three-stage ideal-Delta-U comparison")
    st.write("Stage 1 uses sea-level Is where available; Stages 2 and 3 use vacuum Is. Stage masses are held fixed so the ranking isolates the effect of the book-listed Is values in Eq. (8.24).")

    a,b,c,d=st.columns(4)
    with a:
        payload=st.number_input("Final payload (kg)",min_value=1.0,value=1000.0,step=50.0,key="opt_payload")
    with b:
        mp1=st.number_input("Stage 1 Mp (kg)",min_value=1.0,value=9000.0,step=100.0,key="opt_mp1")
        ms1=st.number_input("Stage 1 Ms (kg)",min_value=1.0,value=1800.0,step=20.0,key="opt_ms1")
    with c:
        mp2=st.number_input("Stage 2 Mp (kg)",min_value=1.0,value=2200.0,step=50.0,key="opt_mp2")
        ms2=st.number_input("Stage 2 Ms (kg)",min_value=1.0,value=500.0,step=10.0,key="opt_ms2")
    with d:
        mp3=st.number_input("Stage 3 Mp (kg)",min_value=1.0,value=650.0,step=20.0,key="opt_mp3")
        ms3=st.number_input("Stage 3 Ms (kg)",min_value=1.0,value=160.0,step=5.0,key="opt_ms3")

    ML3=payload; M03=ML3+ms3+mp3; RM3=M03/(ML3+ms3)
    ML2=M03; M02=ML2+ms2+mp2; RM2=M02/(ML2+ms2)
    ML1=M02; M01=ML1+ms1+mp1; RM1=M01/(ML1+ms1)

    stage1=[k for k,v in BOOK_PROPULSION.items() if v["sea"] is not None]
    upper=[k for k,v in BOOK_PROPULSION.items() if v["vac"] is not None]
    combos=[]
    for p1,p2,p3 in product(stage1,upper,upper):
        Is1=BOOK_PROPULSION[p1]["sea"]; Is2=BOOK_PROPULSION[p2]["vac"]; Is3=BOOK_PROPULSION[p3]["vac"]
        du1=Is1*G0*np.log(RM1); du2=Is2*G0*np.log(RM2); du3=Is3*G0*np.log(RM3)
        combos.append({"Stage 1":p1,"Stage 2":p2,"Stage 3":p3,"Is1":Is1,"Is2":Is2,"Is3":Is3,
                       "Delta U1 (m/s)":du1,"Delta U2 (m/s)":du2,"Delta U3 (m/s)":du3,"Total Delta U (m/s)":du1+du2+du3})
    rank=pd.DataFrame(combos).sort_values("Total Delta U (m/s)",ascending=False).reset_index(drop=True)
    st.dataframe(rank.head(10),use_container_width=True,hide_index=True)
    best=rank.iloc[0]
    st.success(f"Highest ideal Delta U for these fixed masses: {best['Total Delta U (m/s)']/1000:.3f} km/s. Stage 1: {best['Stage 1']}; Stage 2: {best['Stage 2']}; Stage 3: {best['Stage 3']}.")
    st.warning("This is an ideal Delta-U-only comparison, not a complete vehicle optimization. The book states that actual performance varies with motor design. This model also holds stage masses fixed and does not model tank density, gravity loss, drag, steering, or trajectory.")

with tab_eq:
    st.subheader("Equations and calculation walkthrough")
    st.markdown("### Eqs. (8.18)-(8.21)")
    st.latex(r"M_0=M_L+M_s+M_p")
    st.latex(r"M_b=M_L+M_s")
    st.latex(r"\lambda=\frac{M_L}{M_p+M_s}")
    st.latex(r"\epsilon=\frac{M_s}{M_p+M_s}")

    st.markdown("### Eq. (8.23): mass-ratio back-substitution")
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
=rac{1+lambda}{epsilon+lambda}
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

    st.markdown("### Propellant data used")
    st.write("The propellant comparison uses the engine/propellant specific-impulse values in Table 10.2. The book notes that representative propellant performance depends on rocket motor design, so the app does not treat one Is value as universally belonging to a propellant.")

st.divider()
st.caption("Ideal book equations only. Gravity, drag, steering, trajectory losses, and propellant-dependent tank/structure sizing are not included.")
