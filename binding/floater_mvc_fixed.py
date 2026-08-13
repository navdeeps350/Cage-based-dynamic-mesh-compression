import numpy as np
from numba import (
    njit,
    prange,
    get_num_threads,
    get_thread_id,
)


@njit(cache=True, fastmath=False)
def mvc_weights_point_numba_out(p, cage_V, cage_F, w_out, Ehat, En, eps=1e-8):
    """
    Same MVC math as your mvc_weights_point_numba, but writes into w_out (preallocated).
    Ehat (N,3) and En (N,) are workspace buffers (also preallocated).
    """
    N = cage_V.shape[0]
    K = cage_F.shape[0]

    # --- check coincidence with a cage vertex -------------------------
    min_dist  = np.inf
    min_vidx  = 0

    # Ehat, En
    for i in range(N):
        w_out[i] = 0.0
        ex = cage_V[i, 0] - p[0]
        ey = cage_V[i, 1] - p[1]
        ez = cage_V[i, 2] - p[2]
        nrm = np.sqrt(ex*ex + ey*ey + ez*ez)
        En[i] = nrm
        # inv = 1.0 / (nrm)
        # Ehat[i, 0] = ex * inv
        # Ehat[i, 1] = ey * inv
        # Ehat[i, 2] = ez * inv
        if nrm < min_dist:
            min_dist = nrm
            min_vidx = i
    if min_dist < eps:
        # Coincides with a cage vertex -> Kronecker delta.
        w_out[min_vidx] = 1.0
        return  # skip the rest of the computation for this point
    
    for i in range(N):

        inv = 1.0 / En[i]

        Ehat[i, 0] = (cage_V[i, 0] - p[0]) * inv
        Ehat[i, 1] = (cage_V[i, 1] - p[1]) * inv
        Ehat[i, 2] = (cage_V[i, 2] - p[2]) * inv
    
    # faces
    for f in range(K):
        j = cage_F[f, 0]
        k = cage_F[f, 1]
        l = cage_F[f, 2]

        Ejx, Ejy, Ejz = Ehat[j, 0], Ehat[j, 1], Ehat[j, 2]
        Ekx, Eky, Ekz = Ehat[k, 0], Ehat[k, 1], Ehat[k, 2]
        Elx, Ely, Elz = Ehat[l, 0], Ehat[l, 1], Ehat[l, 2]

        # det = dot(Ej, cross(Ek, El))
        cx = Eky*Elz - Ekz*Ely
        cy = Ekz*Elx - Ekx*Elz
        cz = Ekx*Ely - Eky*Elx
        det = Ejx*cx + Ejy*cy + Ejz*cz

        if det == 0.0:
            # Degenerate face (collinear cage vertices) -> skip this face.
            continue

        # of = sign(det)
        of = 0.0
        if det > 0.0:
            of = 1.0
        elif det < 0.0:
            of = -1.0

        # n_jk = unit_normal(Ej, Ek)
        cx = Ejy*Ekz - Ejz*Eky
        cy = Ejz*Ekx - Ejx*Ekz
        cz = Ejx*Eky - Ejy*Ekx
        
        cn = np.sqrt(cx*cx + cy*cy + cz*cz)
        if cn < 1e-10:
            continue

        inv = 1.0 / (cn)
        n_jk_x = of * cx * inv
        n_jk_y = of * cy * inv
        n_jk_z = of * cz * inv

        # skip if any arc is degenerate (returned zero normal)
        # if (n_jk_x==0.0 and n_jk_y==0.0 and n_jk_z==0.0):  # FIX 6
        #     continue


        # n_kl = unit_normal(Ek, El)
        cx = Eky*Elz - Ekz*Ely
        cy = Ekz*Elx - Ekx*Elz
        cz = Ekx*Ely - Eky*Elx

        cn = np.sqrt(cx*cx + cy*cy + cz*cz)
        if cn < 1e-10:
            continue
        inv = 1.0 / (cn)
        n_kl_x = of * cx * inv
        n_kl_y = of * cy * inv
        n_kl_z = of * cz * inv

        # skip if any arc is degenerate (returned zero normal)
        # if (n_kl_x==0.0 and n_kl_y==0.0 and n_kl_z==0.0):  # FIX 6
        #     continue

        # n_lj = unit_normal(El, Ej)
        cx = Ely*Ejz - Elz*Ejy
        cy = Elz*Ejx - Elx*Ejz
        cz = Elx*Ejy - Ely*Ejx
        
        cn = np.sqrt(cx*cx + cy*cy + cz*cz)
        if cn < 1e-10:
            continue

        inv = 1.0 / (cn)
        n_lj_x = of * cx * inv
        n_lj_y = of * cy * inv
        n_lj_z = of * cz * inv

        # skip if any arc is degenerate (returned zero normal)
        # if (n_lj_x==0.0 and n_lj_y==0.0 and n_lj_z==0.0):  # FIX 6
        #     continue

        # angles (no clipping)
        d = Ejx*Ekx + Ejy*Eky + Ejz*Ekz
        if d < -1.0:
            d = -1.0
        elif d > 1.0:
            d = 1.0
        th_jk = np.arccos(d)
        d = Ekx*Elx + Eky*Ely + Ekz*Elz
        if d < -1.0:
            d = -1.0
        elif d > 1.0:
            d = 1.0
        th_kl = np.arccos(d)
        d = Elx*Ejx + Ely*Ejy + Elz*Ejz
        if d < -1.0:
            d = -1.0
        elif d > 1.0:
            d = 1.0
        th_lj = np.arccos(d)

        # m_f
        mf_x = 0.5 * (th_jk*n_jk_x + th_kl*n_kl_x + th_lj*n_lj_x)
        mf_y = 0.5 * (th_jk*n_jk_y + th_kl*n_kl_y + th_lj*n_lj_y)
        mf_z = 0.5 * (th_jk*n_jk_z + th_kl*n_kl_z + th_lj*n_lj_z)

        # mu_j (n_kl, Ej)
        num = n_kl_x*mf_x + n_kl_y*mf_y + n_kl_z*mf_z
        den = n_kl_x*Ejx  + n_kl_y*Ejy  + n_kl_z*Ejz
        if abs(den) < 1e-10:
            mu_j = 0.0
        else:
            mu_j = num / den

        # mu_k (n_lj, Ek)
        num = n_lj_x*mf_x + n_lj_y*mf_y + n_lj_z*mf_z
        den = n_lj_x*Ekx  + n_lj_y*Eky  + n_lj_z*Ekz
        if abs(den) < 1e-10:
            mu_k = 0.0
        else:
            mu_k = num / den

        # mu_l (n_jk, El)
        num = n_jk_x*mf_x + n_jk_y*mf_y + n_jk_z*mf_z
        den = n_jk_x*Elx  + n_jk_y*Ely  + n_jk_z*Elz
        if abs(den) < 1e-10:
            mu_l = 0.0
        else:
            mu_l = num / den

        cj = of * mu_j / (En[j])
        ck = of * mu_k / (En[k])
        cl = of * mu_l / (En[l])

        w_out[j] += cj
        w_out[k] += ck
        w_out[l] += cl

    # # normalize
    # s = 0.0
    # for i in range(N):
    #     s += w_out[i]
    # invs = 1.0 / (s + eps)
    # for i in range(N):
    #     w_out[i] *= invs

    # --- safe normalisation ------------------------------------------
    w_sum = 0.0
    for i in range(N):
        w_sum += w_out[i]

    if abs(w_sum) > eps:               # FIX 7: safe normalisation
        inv = 1.0 / w_sum
        for i in range(N):
            w_out[i] *= inv
    else:
        # Fallback: weight is proportional to 1/distance (Shepard)
        # This fires only for the degenerate vertices identified earlier.
        s = 0.0
        for i in range(N):
            dx = cage_V[i, 0] - p[0]
            dy = cage_V[i, 1] - p[1]
            dz = cage_V[i, 2] - p[2]
            d  = np.sqrt(dx*dx + dy*dy + dz*dz)
            w_out[i] = 1.0 / d if d > eps else 1.0
            s   += w_out[i]
        inv = 1.0 / s
        for i in range(N):
            w_out[i] *= inv



@njit(parallel=True, cache=True, fastmath=True)
def compute_mvc(P, V, F, eps=1e-8):

    m = P.shape[0]
    n = V.shape[0]

    Lam = np.zeros((m, n), dtype=np.float64)

    nt = get_num_threads()

    # One workspace per Numba worker
    Ehat_work = np.zeros((nt, n, 3), dtype=np.float64)
    En_work   = np.zeros((nt, n), dtype=np.float64)

    for t in prange(m):

        tid = get_thread_id()

        Ehat = Ehat_work[tid]
        En   = En_work[tid]

        mvc_weights_point_numba_out(
            P[t],
            V,
            F,
            Lam[t],
            Ehat,
            En,
            eps,
        )

    return Lam