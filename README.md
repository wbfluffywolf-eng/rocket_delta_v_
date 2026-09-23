# Multi-Stage Rocket Velocity-Change Explorer

This Streamlit app follows the notation and staging equations in:

**T.-W. Lee, _Aerospace Propulsion_, Chapter 8**

## Equations used

- Eq. (8.5): `g0 = 9.8066 m/s^2`
- Eq. (8.8): `Ueq = Is * g0`
- Eq. (8.11): `Delta U = Ueq ln(RM) = g0 Is ln(RM)`
- Eq. (8.18): `M0 = ML + Ms + Mp`
- Eq. (8.19): `Mb = ML + Ms`
- Eq. (8.20): `lambda = ML / (Mp + Ms)`
- Eq. (8.21): `epsilon = Ms / (Mp + Ms)`
- Eq. (8.23): `RM = M0/Mb = (1 + lambda)/(epsilon + lambda)`
- Eq. (8.24): `Delta U = sum[Ueq_i ln(RM_i)]`
- Eq. (8.25), similar stages:
  `Delta U = n Ueq ln[(1 + lambda)/(epsilon + lambda)]`

Using Eq. (8.8) in Eq. (8.25):

`Delta U = n Is g0 ln[(1 + lambda)/(epsilon + lambda)]`

## Assignment ranges

- Number of stages, `n`: 1 to 5
- Specific impulse, `Is`: 160 to 385 s
- Payload ratio, `lambda`: 1 to 15%
- Structural mass coefficient, `epsilon`: 18 to 48%

## Run on Windows

1. Install Python 3 from https://www.python.org/downloads/ and check **Add Python to PATH**.
2. Clone this repo:
   ```bash
   git clone https://github.com/wbfluffywolf-eng/rocket_delta_v_.git
   cd rocket_delta_v_
   ```
3. Install packages:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   python -m streamlit run rocket_delta_v_app.py
   ```

The app normally opens at `http://localhost:8501`.

To stop it, press **Ctrl + C** in the terminal.
