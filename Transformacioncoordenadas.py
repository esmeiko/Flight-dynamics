import numpy as np

def BtoV(vx, vy, vz, psi, theta, phi):

    # yaw
    z = np.array([
        [np.cos(psi),  np.sin(psi), 0],
        [-np.sin(psi), np.cos(psi), 0],
        [0, 0, 1]
    ], dtype=float)

    # pitch 
    y = np.array([
        [np.cos(theta), 0, -np.sin(theta)],
        [0, 1, 0],
        [np.sin(theta), 0, np.cos(theta)]
    ], dtype=float)

    # roll
    x = np.array([
        [1, 0, 0],
        [0, np.cos(phi), np.sin(phi)],
        [0, -np.sin(phi), np.cos(phi)]
    ], dtype=float)

    # NED -> Body
    mat = x @ y @ z

    # Body -> NED
    transmat = mat.T

    velocidades = np.array([vx, vy, vz], dtype=float)

    velocidadesned = transmat @ velocidades

    vel = np.linalg.norm(velocidades)

    alpha = np.degrees(np.arctan2(vz, vx))
    beta = np.degrees(np.arcsin(vy/vel))
    gamma = np.degrees(np.arcsin(-velocidadesned[2]/vel))


    return velocidadesned, vel, alpha, beta, gamma, transmat

