import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ------------------------------------------------------------
# Multi-Stage Rocket Velocity-Change Explorer
#
# Source:
# T.-W. Lee, Aerospace Propulsion, Chapter 8:
#   Eq. (8.5):  g0 = 9.8066 m/s^2
#   Eq. (8.8):  Ueq = Is * g0
#   Eq. (8.11): ΔU = Ueq ln(RM) = g0 Is ln(RM)
#   Eq. (8.18): M0 = ML + Ms + Mp
#   Eq. (8.19): Mb = ML + Ms
#   Eq. (8.20): λ = ML / (Mp + Ms)
#   Eq. (8.21): ε = Ms / (Mp + Ms)
#   Eq. (8.23): RM = M0/Mb = (1+λ)/(ε+λ)
#   Eq. (8.24): ΔU = Σ [Ueq,i ln(RM,i)]
#   Eq. (8.25): ΔU = n Ueq ln[(1+λ)/(ε+λ)] for similar stages
#
# Assignment parameter ranges:
#   n: 1–5 stages
#   Is: 160–385 s
#   λ: 1–15%
#   ε: 18–48%
# ------------------------------------------------------------

st.set_page_config(page_title="Multi-Stage Rocket ΔU Explorer", layout="wide")

G0 = 9.8066  # m/s^2, Eq. (8.5)

st.title("🚀 Multi-Stage Rocket Velocity-Change Explorer")
st.caption(
    "Equations and notation follow T.-W. Lee, Aerospace Propulsion, Chapter 8. "
    "Slider limits follow the assignment."
)

with st.expander("Book equations and complete mass-ratio back-substitution", expanded=False):
    st.markdown(r"""
### Book definitions

The initial rocket mass is

\[
M_0=M_L+M_s+M_p
\]

and the burnout mass is

\[
M_b=M_L+M_s
\]

The payload ratio is

\[
\lambda
=
\frac{M_L}{M_0-M_L}
=
\frac{M_L}{M_p+M_s}
\]

The structural mass coefficient is

\[
\epsilon
=
\frac{M_s}{M_p+M_s}
\]

### Back-substitution

Let

\[
S=M_p+M_s
\]

Then, from the definitions above,

\[
M_L=\lambda S
\]

and

\[
M_s=\epsilon S
\]

The initial mass becomes

\[
M_0=M_L+M_s+M_p
\]

Since \(M_s+M_p=S\),

\[
M_0=\lambda S+S
\]

so

\[
M_0=(1+\lambda)S
\]

The burnout mass is

\[
M_b=M_L+M_s
\]

therefore

\[
M_b=\lambda S+\epsilon S
\]

or

\[
M_b=(\lambda+\epsilon)S
\]

Thus,

\[
R_M=\frac{M_0}{M_b}
=
\frac{(1+\lambda)S}{(\epsilon+\lambda)S}
\]

and the common factor \(S\) cancels:

\[
\boxed{
R_M=\frac{1+\lambda}{\epsilon+\lambda}
}
\]

which is Eq. (8.23).

### Specific impulse and equivalent exhaust velocity

From Eq. (8.8),

\[
\boxed{
U_{eq}=I_s g_0
}
\]

where the book gives

\[
g_0=9.8066\ \mathrm{m/s^2}
\]

For one stage, Eq. (8.11) is

\[
\Delta U
=
U_{eq}\ln R_M
=
g_0 I_s\ln R_M
\]

For an arbitrary number of stages, Eq. (8.24) is

\[
\Delta U
=
\sum_{i=1}^{n}
U_{eq,i}\ln R_{M,i}
\]

For the book's "similar stages" assumption,
\(U_{eq,i}=U_{eq}\), \(\epsilon_i=\epsilon\), and \(\lambda_i=\lambda\),
Eq. (8.25) becomes

\[
\boxed{
\Delta U
=
nU_{eq}
\ln\left(\frac{1+\lambda}{\epsilon+\lambda}\right)
}
\]

Using Eq. (8.8),

\[
\boxed{
\Delta U
=
n I_s g_0
\ln\left(\frac{1+\lambda}{\epsilon+\lambda}\right)
}
\]
""")

def mass_ratio(payload_ratio, structural_mass_coefficient):
    """Eq. (8.23)."""
    return (1.0 + payload_ratio) / (
        structural_mass_coefficient + payload_ratio
    )

def equivalent_exhaust_velocity(Is_seconds):
    """Eq. (8.8)."""
    return Is_seconds * G0

def total_delta_u(n, Is_seconds, payload_ratio, structural_mass_coefficient):
    """Eq. (8.25) with Ueq = Is*g0 from Eq. (8.8)."""
    rm = mass_ratio(payload_ratio, structural_mass_coefficient)
    ueq = equivalent_exhaust_velocity(Is_seconds)
    return n * ueq * np.log(rm)

tab1, tab2 = st.tabs([
    "Similar-Stage Rocket Builder",
    "Two-Variable Contour Study"
])

with tab1:
    st.subheader("Similar-stage rocket model")
    st.write(
        "This tab uses the similar-stage form of Eq. (8.25), where each stage "
        "has the same equivalent exhaust velocity, payload ratio, and structural mass coefficient."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        n = st.slider("Number of stages, n", 1, 5, 2, 1)

    with c2:
        Is = st.slider("Specific impulse, Is (s)", 160, 385, 300, 1)

    with c3:
        lambda_pct = st.slider("Payload ratio, λ (%)", 1.0, 15.0, 7.0, 0.1)

    with c4:
        epsilon_pct = st.slider(
            "Structural mass coefficient, ε (%)", 18.0, 48.0, 25.0, 0.1
        )

    lam = lambda_pct / 100.0
    eps = epsilon_pct / 100.0

    RM = mass_ratio(lam, eps)
    Ueq = equivalent_exhaust_velocity(Is)
    delta_u_stage = Ueq * np.log(RM)
    delta_u_total = total_delta_u(n, Is, lam, eps)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mass ratio, RM", f"{RM:.4f}")
    m2.metric("Equivalent exhaust velocity, Ueq", f"{Ueq:,.1f} m/s")
    m3.metric("ΔU per stage", f"{delta_u_stage/1000:.3f} km/s")
    m4.metric("Total ΔU", f"{delta_u_total/1000:.3f} km/s")

    stage_df = pd.DataFrame({
        "Stage, i": np.arange(1, n + 1),
        "Is (s)": [Is] * n,
        "Ueq (m/s)": [Ueq] * n,
        "λ": [lam] * n,
        "ε": [eps] * n,
        "RM": [RM] * n,
        "ΔUi (m/s)": [delta_u_stage] * n,
    })

    st.dataframe(stage_df, use_container_width=True, hide_index=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=stage_df["Stage, i"],
        y=stage_df["ΔUi (m/s)"],
        text=[f"{v/1000:.2f} km/s" for v in stage_df["ΔUi (m/s)"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Velocity-change contribution of each similar stage",
        xaxis_title="Stage, i",
        yaxis_title="ΔUi (m/s)",
        height=430,
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Two-variable parameter study")
    st.write(
        "Choose two assignment variables to vary. The other two are held fixed. "
        "The plotted result is total velocity change, ΔU."
    )

    variables = [
        "Number of stages, n",
        "Specific impulse, Is (s)",
        "Payload ratio, λ (%)",
        "Structural mass coefficient, ε (%)",
    ]

    x_var = st.selectbox("X-axis variable", variables, index=1)
    y_options = [v for v in variables if v != x_var]
    y_var = st.selectbox("Y-axis variable", y_options, index=1)

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        fixed_n = st.slider("Fixed n", 1, 5, 2, 1, key="fixed_n")

    with f2:
        fixed_Is = st.slider("Fixed Is (s)", 160, 385, 300, 1, key="fixed_Is")

    with f3:
        fixed_lambda_pct = st.slider(
            "Fixed λ (%)", 1.0, 15.0, 7.0, 0.1, key="fixed_lambda"
        )

    with f4:
        fixed_epsilon_pct = st.slider(
            "Fixed ε (%)", 18.0, 48.0, 25.0, 0.1, key="fixed_epsilon"
        )

    def axis_values(var):
        if var == "Number of stages, n":
            return np.arange(1, 6, dtype=float)
        if var == "Specific impulse, Is (s)":
            return np.linspace(160, 385, 90)
        if var == "Payload ratio, λ (%)":
            return np.linspace(1, 15, 90)
        if var == "Structural mass coefficient, ε (%)":
            return np.linspace(18, 48, 90)

    x = axis_values(x_var)
    y = axis_values(y_var)
    X, Y = np.meshgrid(x, y)

    N = np.full_like(X, float(fixed_n))
    IS = np.full_like(X, float(fixed_Is))
    LAMBDA_PCT = np.full_like(X, float(fixed_lambda_pct))
    EPSILON_PCT = np.full_like(X, float(fixed_epsilon_pct))

    for var, values in [(x_var, X), (y_var, Y)]:
        if var == "Number of stages, n":
            N = values
        elif var == "Specific impulse, Is (s)":
            IS = values
        elif var == "Payload ratio, λ (%)":
            LAMBDA_PCT = values
        elif var == "Structural mass coefficient, ε (%)":
            EPSILON_PCT = values

    LAMBDA = LAMBDA_PCT / 100.0
    EPSILON = EPSILON_PCT / 100.0

    RM_GRID = (1.0 + LAMBDA) / (EPSILON + LAMBDA)
    UEQ_GRID = IS * G0
    DELTA_U_GRID = N * UEQ_GRID * np.log(RM_GRID) / 1000.0

    contour = go.Figure(data=go.Contour(
        x=x,
        y=y,
        z=DELTA_U_GRID,
        contours=dict(showlabels=True, labelfont=dict(size=11)),
        colorbar=dict(title="ΔU (km/s)"),
    ))

    contour.update_layout(
        title=f"Total ΔU as a function of {x_var} and {y_var}",
        xaxis_title=x_var,
        yaxis_title=y_var,
        height=620,
    )

    st.plotly_chart(contour, use_container_width=True)

    min_index = np.unravel_index(np.nanargmin(DELTA_U_GRID), DELTA_U_GRID.shape)
    max_index = np.unravel_index(np.nanargmax(DELTA_U_GRID), DELTA_U_GRID.shape)

    delta_u_min = float(DELTA_U_GRID[min_index])
    delta_u_max = float(DELTA_U_GRID[max_index])

    r1, r2 = st.columns(2)
    r1.metric("Minimum ΔU in plotted range", f"{delta_u_min:.3f} km/s")
    r2.metric("Maximum ΔU in plotted range", f"{delta_u_max:.3f} km/s")

    summary_df = pd.DataFrame({
        "Point": ["Minimum", "Maximum"],
        "ΔU (km/s)": [delta_u_min, delta_u_max],
        x_var: [X[min_index], X[max_index]],
        y_var: [Y[min_index], Y[max_index]],
    })

    st.dataframe(summary_df, use_container_width=True, hide_index=True)

st.divider()
st.caption(
    "This app evaluates the ideal velocity-change equations presented in Chapter 8. "
    "It does not add gravity, drag, steering, or trajectory losses to the staging equation."
)
