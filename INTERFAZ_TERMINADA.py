import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Transformacioncoordenadas import BtoV

def reset_view():
    ax.view_init(elev=ELEV_INICIAL, azim=AZIM_INICIAL)
    canvas.draw()


root = tk.Tk()
root.title("Task 1 - Coordinate Frames")
frame_main = tk.Frame(root)
frame_main.pack(fill="both", expand=True)


fig = plt.figure(figsize=(7, 7))
ax  = fig.add_subplot(111, projection='3d')
canvas = FigureCanvasTkAgg(fig, master=frame_main)
canvas.get_tk_widget().grid(row=0, column=0, rowspan=20, padx=10, pady=10)
frame_right = tk.Frame(frame_main)
frame_right.grid(row=0, column=1, sticky="n")

ELEV_INICIAL = -150  # negativo para ver con Z (Down) hacia abajo
AZIM_INICIAL = 150  # North al frente, East a la derecha — orientación NED
ax.view_init(elev=ELEV_INICIAL, azim=AZIM_INICIAL)




def get_airplane_points(scale=8):
    s = scale
    segments = [
        # Fuselaje: nariz (+X) → cola (-X)
        np.array([[ s*1.0,  0,     0     ],
                  [-s*0.8,  0,     0     ]]),
        # Ala izquierda (–Y = West)
        np.array([[-s*0.1,  0,     0     ],
                  [-s*0.1, -s,     0     ]]),
        # Ala derecha (+Y = East)
        np.array([[-s*0.1,  0,     0     ],
                  [-s*0.1,  s,     0     ]]),
        # Deriva vertical (–Z = Up en NED)
        np.array([[-s*0.6,  0,     0     ],
                  [-s*0.6,  0,    -s*0.4 ]]),
    ]
    return segments


def draw_airplane(ax, psi, theta, phi, scale=8):
    """Rota y dibuja el avioncito en el espacio NED."""

    Rz = np.array([[np.cos(psi),  np.sin(psi), 0],
                   [-np.sin(psi), np.cos(psi), 0],
                   [0,            0,           1]])

    Ry = np.array([[np.cos(theta),  0, -np.sin(theta)],
                   [0,              1,  0],
                   [np.sin(theta),  0,  np.cos(theta)]])

    Rx = np.array([[1,  0,           0],
                   [0,  np.cos(phi), np.sin(phi)],
                   [0, -np.sin(phi), np.cos(phi)]])

    R = (Rx @ Ry @ Rz).T

    for seg in get_airplane_points(scale):
        pts = np.array([R @ p for p in seg])
        ax.plot(pts[:, 0], pts[:, 1], pts[:, 2],
                color='darkorange', linewidth=2.5)



def update(val=None):
    try:
        vx = float(entry_vx.get())
        vy = float(entry_vy.get())
        vz = float(entry_vz.get())
    except ValueError:
        return

    psi   = np.radians(psi_slider.get())
    theta = np.radians(theta_slider.get())
    phi   = np.radians(phi_slider.get())

    velocidadesned, vel, alpha, beta, gamma, transmat = BtoV(vx, vy, vz, psi, theta, phi)

    elev_actual = ax.elev
    azim_actual = ax.azim
    ax.cla()
    ax.view_init(elev=elev_actual, azim=azim_actual)
    ax.invert_zaxis()   

    longitud = 15

    # Ejes NED
    ax.quiver(0,0,0, longitud,0,0, color='gray', linewidth=1, arrow_length_ratio=0.1)
    ax.quiver(0,0,0, 0,longitud,0, color='gray', linewidth=1, arrow_length_ratio=0.1)
    ax.quiver(0,0,0, 0,0,longitud, color='gray', linewidth=1, arrow_length_ratio=0.1)
    ax.text(longitud, 0, 0, 'N', color='gray')
    ax.text(0, longitud, 0, 'E', color='gray')
    ax.text(0, 0, longitud, 'D', color='gray')

    # Vector velocidades
    ax.quiver(0,0,0, vx,vy,vz,
              color='royalblue', linewidth=2, arrow_length_ratio=0.1,
              label='Velocidad |V|')

    # Vector NED transformado 
    ax.quiver(0,0,0,
              velocidadesned[0], velocidadesned[1], velocidadesned[2],
              color='limegreen', linewidth=2, arrow_length_ratio=0.1,
              label='Vector transformado a NED')

    # Avioncito 
    scale_avion = max(5, vel * 0.15)
    draw_airplane(ax, psi, theta, phi, scale=scale_avion)

    limite = max(10, abs(vx), abs(vy), abs(vz),
                 abs(velocidadesned[0]),
                 abs(velocidadesned[1]),
                 abs(velocidadesned[2]))

    ax.set_xlim([-limite, limite])
    ax.set_ylim([-limite, limite])
    ax.set_zlim([-limite, limite])

    ax.set_xlabel("North (X)")
    ax.set_ylabel("East (Y)")
    ax.set_zlabel("Down (Z)")
    ax.legend(loc='upper left', fontsize=8)

    ned_txt = (f"V_NED = [{velocidadesned[0]:7.3f}, "
            f"{velocidadesned[1]:7.3f}, "
            f"{velocidadesned[2]:7.3f}] m/s")

    tm = transmat

    info_txt = (
        f"|V| = {vel:.2f} m/s        T_body→NED = [{tm[0,0]:7.2f}  {tm[0,1]:7.2f}  {tm[0,2]:7.2f}]\n"
        f"α = {alpha:.2f}°                           [{tm[1,0]:7.2f}  {tm[1,1]:7.2f}  {tm[1,2]:7.2f}]\n"
        f"β = {beta:.2f}°                           [{tm[2,0]:7.2f}  {tm[2,1]:7.2f}  {tm[2,2]:7.2f}]\n"
        f"γ = {gamma:.2f}°\n\n"
       f"{ned_txt}"
    )

    label_info.config(
        text=info_txt,
        font=("Courier", 10),  # importante: fuente monoespaciada
        justify="left"
    )
    
    canvas.draw()


frame_inputs = tk.Frame(frame_right)
frame_inputs.pack(pady=5)

tk.Label(frame_inputs, text="u (vx)").grid(row=0, column=0)
entry_vx = tk.Entry(frame_inputs, width=6)
entry_vx.insert(0, "50")
entry_vx.grid(row=0, column=1)

tk.Label(frame_inputs, text="v (vy)").grid(row=0, column=2)
entry_vy = tk.Entry(frame_inputs, width=6)
entry_vy.insert(0, "0")
entry_vy.grid(row=0, column=3)

tk.Label(frame_inputs, text="w (vz)").grid(row=0, column=4)
entry_vz = tk.Entry(frame_inputs, width=6)
entry_vz.insert(0, "0")
entry_vz.grid(row=0, column=5)

tk.Button(frame_right, text="Actualizar", command=update).pack(pady=5)



psi_slider = tk.Scale(frame_right, from_=0, to=360, orient=tk.HORIZONTAL,
                      label="Yaw ψ", command=update)
psi_slider.pack(fill="x")

theta_slider = tk.Scale(frame_right, from_=0, to=360, orient=tk.HORIZONTAL,
                        label="Pitch θ", command=update)
theta_slider.pack(fill="x")

phi_slider = tk.Scale(frame_right, from_=0, to=360, orient=tk.HORIZONTAL,
                      label="Roll ϕ", command=update)
phi_slider.pack(fill="x")


def case_straight():
    entry_vx.delete(0, tk.END); entry_vx.insert(0, "60")
    entry_vy.delete(0, tk.END); entry_vy.insert(0, "0")
    entry_vz.delete(0, tk.END); entry_vz.insert(0, "0")
    psi_slider.set(0); theta_slider.set(0); phi_slider.set(0)
    update()

def case_climb():
    entry_vx.delete(0, tk.END); entry_vx.insert(0, "60")
    entry_vy.delete(0, tk.END); entry_vy.insert(0, "0")
    entry_vz.delete(0, tk.END); entry_vz.insert(0, "-15")
    psi_slider.set(0); theta_slider.set(15); phi_slider.set(0)
    update()

def case_turn():
    entry_vx.delete(0, tk.END); entry_vx.insert(0, "50")
    entry_vy.delete(0, tk.END); entry_vy.insert(0, "-10")
    entry_vz.delete(0, tk.END); entry_vz.insert(0, "0")
    psi_slider.set(30); theta_slider.set(0); phi_slider.set(25)
    update()

frame_cases = tk.Frame(frame_right)
frame_cases.pack(pady=5)

tk.Button(frame_cases, text="Case A: Straight & Level", command=case_straight).grid(row=0, column=0)
tk.Button(frame_cases, text="Case B: Climb",            command=case_climb).grid(row=0, column=1)
tk.Button(frame_cases, text="Case C: Turn",             command=case_turn).grid(row=0, column=2)
tk.Button(frame_right, text="Regresar a Vista Inicial", command=reset_view).pack(pady=5)


label_info = tk.Label(frame_right,
                      text="",
                      font=("Courier", 10),
                      justify="left")
label_info.pack(pady=10)
update()
root.mainloop()
