-- coding: utf-8 --
"""
Berramdane Model V8.2 – Enhanced Visualization (7 peaks, Loss Map, Phase Map)
نموذج "بالرمضان" – نسخة معززة بصرياً (7 قمم، خريطة الضياع، طور دوامي)

Author : Al Moalim Berramdane
License: CC BY 4.0
"""

import numpy as np
import matplotlib.pyplot as plt

============================================================
1. Constants and calibrated parameters (7 peaks, stable)
============================================================
h = 6.626e-34
hbar = h / (2 * np.pi)
m = 9.109e-31
e = 1.6e-19
c = 3e8
m_c2 = m * c**2
omega_Compton = m_c2 / hbar

Slit geometry (gives n_side ≈ 3 → 7 peaks)
a_width = 0.72e-6
d_slit = 2.45e-6
L_total = 2.2
v_nominal = 5.8e5
delta_v = 0.02 * v_nominal
n_velocities = 100

Medium (lens) – adjusted to give high maturity (L_focus ~1.5 m)
rho_medium = 1.5e-15
nu_medium = 1.5e-6
k_lens = 1.0e-21
L_focus = k_lens * (d_slit / a_width) / (nu_medium * rho_medium)

Observer and magnetic effects (disabled for clean pattern)
observer_active = False
use_magnetic_splitting = False

Tunneling parameters (same as V8.1)
wall_density = 1.0
barrier_thickness = 0.5e-9
V0_max = 3.1 * e
V0_min = 0.0
electron_energy = 1.5 * e

============================================================
2. Core functions (unchanged, dynamic peak count)
============================================================
def de_broglie_wavelength(v):
return h / (m * v)

def diffraction_angle(v):
lam = de_broglie_wavelength(v)
return np.arctan(lam / a_width)

def number_of_engagement_points(v_par, L):
lam = de_broglie_wavelength(v_par)
theta = diffraction_angle(v_par)
tan_theta = np.tan(theta)
spread = tan_theta * L
spacing = lam * L / d_slit
n_side_float = spread / spacing
maturity = np.tanh(L / L_focus)
n_side_float *= maturity
n_side = max(1, int(round(n_side_float)))
return 1 + 2 * n_side, n_side

def cone_centers(v_par, L):
lam = de_broglie_wavelength(v_par)
spacing = lam * L / d_slit
_, n_side = number_of_engagement_points(v_par, L)
centers = np.linspace(-n_side * spacing, n_side * spacing, 2*n_side + 1)
return centers, spacing

def cone_intensity(x, center, sigma):
return np.exp(-(x - center)2 / (2 * sigma2))

def double_slit_intensity(x, v_par, L):
centers, spacing = cone_centers(v_par, L)
sigma = spacing / 3.5
I_base = np.zeros_like(x)
for c in centers:
I_base += cone_intensity(x, c, sigma)
lam = de_broglie_wavelength(v_par)
beta = (np.pi * d_slit * x) / (lam * L)
alpha = (np.pi * a_width * x) / (lam * L)
envelope = np.cos(beta)2 * np.sinc(alpha / np.pi) 2
maturity = np.tanh(L / L_focus)
return I_base * envelope * maturity

def tunneling_probability(v_par, V0, thickness):
E_kin = 0.5 * m * v_par2
if E_kin >= V0:
return 1.0
kappa = np.sqrt(2 * m * (V0 - E_kin)) / hbar
gamow = np.exp(-2 * kappa * thickness)
omega_spin = 2 * np.pi * a_width * m2 * v_par3 / h2
drill = np.tanh(omega_spin / omega_Compton)
return gamow * drill

============================================================
3. Main simulation
============================================================
x = np.linspace(-0.005, 0.005, 1200)
velocities = np.random.normal(v_nominal, delta_v, n_velocities)
velocities = np.clip(velocities, v_nominal - 3delta_v, v_nominal + 3delta_v)

total_intensity = np.zeros_like(x)
for v in velocities:
total_intensity += double_slit_intensity(x, v, L_total)
total_intensity /= n_velocities
total_intensity /= np.max(total_intensity)

Loss map (particles that are "crushed" – energy not reaching the screen)
For visualization, loss is simply 1 - intensity (places where particles are missing)
loss_map = 1 - total_intensity

Simple phase map (arctan of envelope vs. base? For illustration only)
To give a "vortex" impression, we can plot the argument of a complex signal
Here we use the phase of the analytical signal from Hilbert transform (optional)
For simplicity, we use the sign of the derivative to highlight nodes.
phase_map = np.gradient(total_intensity, x)

Compute average peak count and visibility
peak_counts = []
for v in velocities:
_, n_side = number_of_engagement_points(v, L_total)
peak_counts.append(1 + 2 * n_side)
avg_peaks = np.mean(peak_counts)

I_max = np.max(total_intensity)
center_idx = np.argmin(np.abs(x))
I_min = np.min(total_intensity[center_idx-40:center_idx+40])
visibility = (I_max - I_min) / (I_max + I_min) if (I_max+I_min)>0 else 0

Tunneling example
v_t = np.sqrt(2 * electron_energy / m)
V0_eff = V0_min + wall_density * (V0_max - V0_min)
T_model = tunneling_probability(v_t, V0_eff, barrier_thickness)
kappa_qm = np.sqrt(2 * m * (V0_eff - electron_energy)) / hbar
T_qm = np.exp(-2 * kappa_qm * barrier_thickness)
drill = T_model / T_qm if T_qm != 0 else 0

============================================================
4. Plots – 6 scenes (interference, screen, tunneling, decay, loss map, phase)
============================================================
plt.figure(figsize=(18, 12))

Scene 1: 7 peaks pattern
plt.subplot(2, 3, 1)
plt.plot(x * 1000, total_intensity, 'b-', lw=2)
plt.fill_between(x * 1000, total_intensity, alpha=0.3)
plt.title(f'7 Peaks Pattern (avg peaks = {avg_peaks:.1f})')
plt.xlabel('Position (mm)')
plt.ylabel('Intensity (a.u.)')
plt.xlim(-5, 5)
plt.grid(True, alpha=0.3)

Scene 2: Real screen view (2D vertical fringes)
plt.subplot(2, 3, 2)
screen = np.tile(total_intensity, (200, 1))
plt.imshow(screen, cmap='Blues', aspect='auto', extent=[-5, 5, 0, 1])
plt.colorbar(label='Intensity')
plt.title('Real Screen View')
plt.xlabel('Position (mm)')
plt.yticks([])

Scene 3: Hybrid tunneling vs wall density
plt.subplot(2, 3, 3)
densities = np.linspace(0, 1, 200)
probs = [tunneling_probability(v_t, V0_min + d*(V0_max-V0_min), barrier_thickness) for d in densities]
plt.plot(densities, probs, 'r-', lw=2)
plt.title('Hybrid Tunneling (Gamow × Drill)')
plt.xlabel('Wall density')
plt.ylabel('Probability')
plt.grid(True, alpha=0.3)

Scene 4: Exponential decay (Gamow factor)
plt.subplot(2, 3, 4)
thicknesses = np.linspace(0.5e-9, 5e-9, 100)
prob_thick = [tunneling_probability(v_t, V0_eff, t) for t in thicknesses]
plt.semilogy(thicknesses*1e9, prob_thick, 'g-', lw=2)
plt.title('Exponential Decay (Gamow)')
plt.xlabel('Thickness (nm)')
plt.ylabel('Probability (log)')
plt.grid(True, alpha=0.3)

Scene 5: Loss Map (where particles are "crushed")
plt.subplot(2, 3, 5)
plt.plot(x * 1000, loss_map, 'r-', lw=2, label='Loss intensity')
plt.fill_between(x * 1000, loss_map, alpha=0.3, color='red')
plt.title('Loss Map (crushed particles / energy dissipation)')
plt.xlabel('Position (mm)')
plt.ylabel('Loss (a.u.)')
plt.xlim(-5, 5)
plt.grid(True, alpha=0.3)

Scene 6: Phase map (to suggest vortex structure)
plt.subplot(2, 3, 6)
Use a simple color map of the derivative (gradient) to indicate phase change
phase_plot = np.tile(phase_map, (100, 1))
plt.imshow(phase_plot, cmap='RdBu', aspect='auto', extent=[-5, 5, 0, 1])
plt.colorbar(label='Phase gradient')
plt.title('Vortex Phase Map (gradient of intensity)')
plt.xlabel('Position (mm)')
plt.yticks([])

plt.suptitle('Berramdane Model V8.2 – Enhanced Visualization (Loss Map & Phase Map)', fontsize=16)
plt.tight_layout()
plt.show()

============================================================
5. Console report
============================================================
print("="*70)
print("Berramdane Model V8.2 – Stable core with additional visualizations")
print("="70)
print(f"Wavelength λ = {h/(mv_nominal)1e9:.2f} nm")
print(f"Peak spacing = {h/(mv_nominal)L_total/d_slit1000:.2f} mm")
print(f"Average number of visible peaks: {avg_peaks:.1f} (dynamic, ~7)")
print(f"Fringe visibility: {visibility:.1%}")
print("\n--- Tunneling (1.5 eV, 3.1 eV barrier, 0.5 nm) ---")
print(f"Berramdane: T = {T_model:.3e}")
print(f"Standard QM: T = {T_qm:.3e}")
print(f"Drill factor D = {drill:.3e}")
print(f"Ratio (model/QM) = {T_model/T_qm:.3f}")
print("\nAdditional visualizations explained:")
print("- Loss Map: shows where particles are 'crushed' (energy not reaching the screen).")
print("- Phase Map: indicates vortex‑like structure (gradient of the intensity).")
print("These are for illustration; the core physics remains unchanged.")
print("\nLimitations (as in V8.1):")
print("- Model is local (S=2). No Bell violation.")
print("- Tunneling is hybrid (Gamow factor from QM).")
print("- Viscous medium is phenomenological.")
print("="*70)