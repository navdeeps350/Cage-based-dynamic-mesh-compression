import numpy as np
from numba import njit, prange
from numba.typed import Dict
from numba import types


# =============================================================================
# 1.  3D Mean Value Coordinates  (Ju, Schaefer & Warren 2005)
# =============================================================================


import numpy as np
from numba import njit, prange


# @njit(cache=True, fastmath=True)
# def mvc_3d_single_into(x, V, F, eps, lam):
#     """
#     Compute 3D MVC weights of point x w.r.t. mesh (V, F) into lam (length n).
#     lam is zeroed inside; on a vertex coincidence or in-face hit, only the
#     relevant entries are nonzero.
#     """
#     n = V.shape[0]
#     nf = F.shape[0]

#     # Zero output (callers reuse rows of a matrix).
#     for i in range(n):
#         lam[i] = 0.0

#     # Per-vertex distances and unit directions from x.
#     dist = np.empty(n)
#     u = np.empty((n, 3))
#     min_dist = np.inf
#     min_idx = 0
#     for i in range(n):
#         dx = V[i, 0] - x[0]
#         dy = V[i, 1] - x[1]
#         dz = V[i, 2] - x[2]
#         di = np.sqrt(dx * dx + dy * dy + dz * dz)
#         dist[i] = di
#         if di < min_dist:
#             min_dist = di
#             min_idx = i
#         inv = 1.0 / di if di > 0.0 else 0.0
#         u[i, 0] = dx * inv
#         u[i, 1] = dy * inv
#         u[i, 2] = dz * inv

#     # Coincides with a cage vertex -> Kronecker delta.
#     if min_dist < eps:
#         lam[min_idx] = 1.0
#         return

#     total = 0.0
#     for fi in range(nf):
#         i1 = F[fi, 0]
#         i2 = F[fi, 1]
#         i3 = F[fi, 2]

#         u1x = u[i1, 0]; u1y = u[i1, 1]; u1z = u[i1, 2]
#         u2x = u[i2, 0]; u2y = u[i2, 1]; u2z = u[i2, 2]
#         u3x = u[i3, 0]; u3y = u[i3, 1]; u3z = u[i3, 2]

#         d1 = dist[i1]
#         d2 = dist[i2]
#         d3 = dist[i3]

#         # Chord lengths between u_i, u_j on S^2.
#         ex = u2x - u3x; ey = u2y - u3y; ez = u2z - u3z
#         l1 = np.sqrt(ex * ex + ey * ey + ez * ez)
#         ex = u3x - u1x; ey = u3y - u1y; ez = u3z - u1z
#         l2 = np.sqrt(ex * ex + ey * ey + ez * ez)
#         ex = u1x - u2x; ey = u1y - u2y; ez = u1z - u2z
#         l3 = np.sqrt(ex * ex + ey * ey + ez * ez)

#         a1 = 0.5 * l1
#         if a1 > 1.0: a1 = 1.0
#         elif a1 < -1.0: a1 = -1.0
#         theta1 = 2.0 * np.arcsin(a1)

#         a2 = 0.5 * l2
#         if a2 > 1.0: a2 = 1.0
#         elif a2 < -1.0: a2 = -1.0
#         theta2 = 2.0 * np.arcsin(a2)

#         a3 = 0.5 * l3
#         if a3 > 1.0: a3 = 1.0
#         elif a3 < -1.0: a3 = -1.0
#         theta3 = 2.0 * np.arcsin(a3)

#         h = 0.5 * (theta1 + theta2 + theta3)

#         # x lies on the plane of f, inside f -> 2D barycentric on this face.
#         if np.pi - h < eps:
#             w1 = np.sin(theta1) * d2 * d3
#             w2 = np.sin(theta2) * d3 * d1
#             w3 = np.sin(theta3) * d1 * d2
#             tot = w1 + w2 + w3
#             for k in range(n):
#                 lam[k] = 0.0
#             lam[i1] = w1 / tot
#             lam[i2] = w2 / tot
#             lam[i3] = w3 / tot
#             return

#         sin_h = np.sin(h)
#         sin_t1 = np.sin(theta1)
#         sin_t2 = np.sin(theta2)
#         sin_t3 = np.sin(theta3)

#         c1 = (2.0 * sin_h * np.sin(h - theta1)) / (sin_t2 * sin_t3) - 1.0
#         c2 = (2.0 * sin_h * np.sin(h - theta2)) / (sin_t3 * sin_t1) - 1.0
#         c3 = (2.0 * sin_h * np.sin(h - theta3)) / (sin_t1 * sin_t2) - 1.0

#         # det([u1; u2; u3]) inlined.
#         det = (u1x * (u2y * u3z - u2z * u3y)
#              - u1y * (u2x * u3z - u2z * u3x)
#              + u1z * (u2x * u3y - u2y * u3x))
#         sgn = 1.0 if det >= 0.0 else -1.0

#         v1 = 1.0 - c1 * c1
#         v2 = 1.0 - c2 * c2
#         v3 = 1.0 - c3 * c3
#         if v1 < 0.0: v1 = 0.0
#         if v2 < 0.0: v2 = 0.0
#         if v3 < 0.0: v3 = 0.0
#         s1 = sgn * np.sqrt(v1)
#         s2 = sgn * np.sqrt(v2)
#         s3 = sgn * np.sqrt(v3)

#         if abs(s1) < eps or abs(s2) < eps or abs(s3) < eps:
#             # x on plane of f but outside the face -> ignore this face.
#             continue

#         w1 = (theta1 - c2 * theta3 - c3 * theta2) / (d1 * sin_t2 * s3)
#         w2 = (theta2 - c3 * theta1 - c1 * theta3) / (d2 * sin_t3 * s1)
#         w3 = (theta3 - c1 * theta2 - c2 * theta1) / (d3 * sin_t1 * s2)

#         lam[i1] += w1
#         lam[i2] += w2
#         lam[i3] += w3
#         total += w1 + w2 + w3

#     inv = 1.0 / total
#     for i in range(n):
#         lam[i] *= inv


# @njit(cache=True, fastmath=True)
# def mvc_3d_single(x, V, F, eps=1e-8):
#     """Allocating wrapper, matches the original signature."""
#     lam = np.empty(V.shape[0])
#     mvc_3d_single_into(x, V, F, eps, lam)
#     return lam


@njit(cache=True, fastmath=True)
def mvc_3d_single_into(x, V, F, eps, lam, Ehat=None, En=None):
    """
    Compute 3D MVC weights of point x w.r.t. mesh (V, F) into lam (length n).
    lam is zeroed inside; on a vertex coincidence or in-face hit, only the
    relevant entries are nonzero.
    """
    n = V.shape[0]
    nf = F.shape[0]

    # Zero output (callers reuse rows of a matrix).
    for i in range(n):
        lam[i] = 0.0

    # Per-vertex distances and unit directions from x.
    if Ehat is None:
        Ehat = np.empty((n, 3))
    if En is None:
        En = np.empty(n)
    # dist = np.empty(n)
    # u = np.empty((n, 3))
    min_dist = np.inf
    min_idx = 0
    for i in range(n):
        dx = V[i, 0] - x[0]
        dy = V[i, 1] - x[1]
        dz = V[i, 2] - x[2]
        di = np.sqrt(dx * dx + dy * dy + dz * dz)
        En[i] = di
        if di < min_dist:
            min_dist = di
            min_idx = i
        inv = 1.0 / di if di > 0.0 else 0.0
        Ehat[i, 0] = dx * inv
        Ehat[i, 1] = dy * inv
        Ehat[i, 2] = dz * inv

    # Coincides with a cage vertex -> Kronecker delta.
    if min_dist < eps:
        lam[min_idx] = 1.0
        return

    total = 0.0
    for fi in range(nf):
        i1 = F[fi, 0]
        i2 = F[fi, 1]
        i3 = F[fi, 2]

        u1x = Ehat[i1, 0]; u1y = Ehat[i1, 1]; u1z = Ehat[i1, 2]
        u2x = Ehat[i2, 0]; u2y = Ehat[i2, 1]; u2z = Ehat[i2, 2]
        u3x = Ehat[i3, 0]; u3y = Ehat[i3, 1]; u3z = Ehat[i3, 2]

        d1 = En[i1]
        d2 = En[i2]
        d3 = En[i3]

        # Chord lengths between u_i, u_j on S^2.
        ex = u2x - u3x; ey = u2y - u3y; ez = u2z - u3z
        l1 = np.sqrt(ex * ex + ey * ey + ez * ez)
        ex = u3x - u1x; ey = u3y - u1y; ez = u3z - u1z
        l2 = np.sqrt(ex * ex + ey * ey + ez * ez)
        ex = u1x - u2x; ey = u1y - u2y; ez = u1z - u2z
        l3 = np.sqrt(ex * ex + ey * ey + ez * ez)

        a1 = 0.5 * l1
        if a1 > 1.0: a1 = 1.0
        elif a1 < -1.0: a1 = -1.0
        theta1 = 2.0 * np.arcsin(a1)

        a2 = 0.5 * l2
        if a2 > 1.0: a2 = 1.0
        elif a2 < -1.0: a2 = -1.0
        theta2 = 2.0 * np.arcsin(a2)

        a3 = 0.5 * l3
        if a3 > 1.0: a3 = 1.0
        elif a3 < -1.0: a3 = -1.0
        theta3 = 2.0 * np.arcsin(a3)

        h = 0.5 * (theta1 + theta2 + theta3)

        # x lies on the plane of f, inside f -> 2D barycentric on this face.
        if np.pi - h < eps:
            w1 = np.sin(theta1) * d2 * d3
            w2 = np.sin(theta2) * d3 * d1
            w3 = np.sin(theta3) * d1 * d2
            tot = w1 + w2 + w3
            for k in range(n):
                lam[k] = 0.0
            lam[i1] = w1 / tot
            lam[i2] = w2 / tot
            lam[i3] = w3 / tot
            return

        sin_h = np.sin(h)
        sin_t1 = np.sin(theta1)
        sin_t2 = np.sin(theta2)
        sin_t3 = np.sin(theta3)

        c1 = (2.0 * sin_h * np.sin(h - theta1)) / (sin_t2 * sin_t3) - 1.0
        c2 = (2.0 * sin_h * np.sin(h - theta2)) / (sin_t3 * sin_t1) - 1.0
        c3 = (2.0 * sin_h * np.sin(h - theta3)) / (sin_t1 * sin_t2) - 1.0

        # det([u1; u2; u3]) inlined.
        det = (u1x * (u2y * u3z - u2z * u3y)
             - u1y * (u2x * u3z - u2z * u3x)
             + u1z * (u2x * u3y - u2y * u3x))
        sgn = 1.0 if det >= 0.0 else -1.0

        v1 = 1.0 - c1 * c1
        v2 = 1.0 - c2 * c2
        v3 = 1.0 - c3 * c3
        if v1 < 0.0: v1 = 0.0
        if v2 < 0.0: v2 = 0.0
        if v3 < 0.0: v3 = 0.0
        s1 = sgn * np.sqrt(v1)
        s2 = sgn * np.sqrt(v2)
        s3 = sgn * np.sqrt(v3)

        if abs(s1) < eps or abs(s2) < eps or abs(s3) < eps:
            # x on plane of f but outside the face -> ignore this face.
            continue

        w1 = (theta1 - c2 * theta3 - c3 * theta2) / (d1 * sin_t2 * s3)
        w2 = (theta2 - c3 * theta1 - c1 * theta3) / (d2 * sin_t3 * s1)
        w3 = (theta3 - c1 * theta2 - c2 * theta1) / (d3 * sin_t1 * s2)

        lam[i1] += w1
        lam[i2] += w2
        lam[i3] += w3
        total += w1 + w2 + w3

    inv = 1.0 / total
    for i in range(n):
        lam[i] *= inv


@njit(cache=True, fastmath=True)
def mvc_weights_point_numba_out(p, cage_V, cage_F, lam, Ehat=None, En=None, eps=1e-8):
    """Allocating wrapper, matches the original signature."""
    lam = np.empty(cage_V.shape[0])
    mvc_3d_single_into(p, cage_V, cage_F, eps, lam, Ehat=Ehat, En=En)
    return lam


@njit(parallel=True, cache=True, fastmath=True)
def compute_mvc(P, V, F, eps=1e-8, Ehat=None, En=None):
    """
    Build Lambda where Lambda[t, i] = lambda_i(P[t]). Rows computed in parallel.
    """
    m = P.shape[0]
    n = V.shape[0]
    Lam = np.empty((m, n))
    for t in prange(m):
        mvc_3d_single_into(P[t], V, F, eps, Lam[t], Ehat=Ehat, En=En)
    return Lam