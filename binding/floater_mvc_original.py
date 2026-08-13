# =============================================================================
# 1.  3D Mean Value Coordinates  (Floater)
# =============================================================================



import numpy as np
from numba import njit, prange
from numba.typed import Dict
from numba import types



# Define specific types for Numba
float_array = types.float64[:,:]
int_array = types.int64[:,:]
vec_type = types.float64[:]
tuple_type = types.Tuple((vec_type, types.float64))

@njit(nopython=True)
def compute_unit_vector(i, p, c, coverage_dict):
    if i in coverage_dict:
        e = coverage_dict[i][0]
        norm_e = coverage_dict[i][1]
    else:
        e = c - p
        norm_e = np.linalg.norm(e)
        coverage_dict[i] = (e, norm_e)
    return e, norm_e

@njit(nopython=True)
def compute_orientation(ej, ek, el):
    matrix = np.empty((3, 3))
    matrix[:, 0] = ej
    matrix[:, 1] = ek
    matrix[:, 2] = el
    of = np.sign(np.linalg.det(matrix))
    return of

@njit(nopython=True)
def compute_normal(of, e1, e2):
    cross = np.cross(e1, e2)
    norm = np.linalg.norm(cross)
    n = of * cross / norm
    return n

@njit(nopython=True)
def compute_theta(e1, e2):
    cos_theta = np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2))
    # cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)
    return theta

@njit(nopython=True)
def compute_m(theta_1, theta_2, theta_3, n_1, n_2, n_3):
    m = 0.5 * (theta_1 * n_1 + theta_2 * n_2 + theta_3 * n_3)
    return m

@njit(nopython=True)
def compute_mu(n, m, e):
    mu = np.dot(n, m) / np.dot(n, e)
    return mu

@njit(nopython=True, parallel=True, cache=True)
def compute_mvc(mesh_vertices, cage_vertices, cage_faces):
    M = mesh_vertices.shape[0]
    N = cage_vertices.shape[0]
    mvc_weights = np.zeros((M, N))
    
    for m_idx in prange(M):
        x = mesh_vertices[m_idx]
        coverage_dict = Dict.empty(
            key_type=types.int64,
            value_type=tuple_type
        )
        w = np.zeros(N)
        
        for face in cage_faces:
            j, k, l = face
            c_j = cage_vertices[j]
            c_k = cage_vertices[k]
            c_l = cage_vertices[l]
            
            e_j, norm_ej = compute_unit_vector(j, x, c_j, coverage_dict)
            e_k, norm_ek = compute_unit_vector(k, x, c_k, coverage_dict)
            e_l, norm_el = compute_unit_vector(l, x, c_l, coverage_dict)
            
            e_j = e_j / norm_ej
            e_k = e_k / norm_ek
            e_l = e_l / norm_el
            
            o_f = compute_orientation(e_j, e_k, e_l)
            
            n_jk = compute_normal(o_f, e_j, e_k)
            n_kl = compute_normal(o_f, e_k, e_l)
            n_lj = compute_normal(o_f, e_l, e_j)
            
            theta_jk = compute_theta(e_j, e_k)
            theta_kl = compute_theta(e_k, e_l)
            theta_lj = compute_theta(e_l, e_j)
            
            m_f = compute_m(theta_jk, theta_kl, theta_lj, n_jk, n_kl, n_lj)
            
            mu_j = compute_mu(n_kl, m_f, e_j)
            mu_k = compute_mu(n_lj, m_f, e_k)
            mu_l = compute_mu(n_jk, m_f, e_l)
            
            w[j] += o_f * mu_j / norm_ej
            w[k] += o_f * mu_k / norm_ek
            w[l] += o_f * mu_l / norm_el
        
        w /= np.sum(w)
        mvc_weights[m_idx] = w
    
    return mvc_weights
