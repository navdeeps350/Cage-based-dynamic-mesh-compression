import subprocess
import os
import trimesh
import numpy as np
# from utils_numba import compute_mvc
from binding.floater_mvc_fixed import mvc_weights_point_numba_out, compute_mvc
# from binding.floater_mvc import compute_mvc_matrix as compute_mvc, mvc_3d_single_into

import igl

from utils_1 import RemappedCageFile, obj_to_off
from utils_2 import RemappedCageFolder, average_edge_length

import shutil
from pathlib import Path
import subprocess, os

from meshplot import plot

import numpy as np
import time

import numpy as np
from numba import njit, prange


wd = os.getcwd()


# mx.set_default_device(mx.cpu)  # force all ops to run on CPU
workdir = f"{wd}/Dynamic mesh codec for mac v2"


action = "bouncing"  # Change this to the desired action
alpha = 2.75 # This can be adjusted as needed
parameter_avg_mesh = 0.001  # This can be adjusted as needed

alpha_str = str(alpha).replace(".", "_")


mesh_avg_vert, mesh_avg_fac = igl.read_triangle_mesh(f"avg_meshes/{action}Avg.obj")
cage_avg_vert, cage_avg_fac = igl.read_triangle_mesh(f"avg_meshes/{action}Avg_cage.obj")


mesh_avg_length = average_edge_length(mesh_avg_vert, mesh_avg_fac)
cage_avg_length = average_edge_length(cage_avg_vert, cage_avg_fac)



import shutil
from pathlib import Path
import subprocess, os

def run_laplace_avgmesh(
    executable: str = "./LaplaceMeshCodec",
    mode: str = "-ea",
    out_file: str = "avgMesh.obj",
    workdir: str | None = None,
) -> subprocess.CompletedProcess:

    exe_path = Path(executable)


    cmd = [
        str(exe_path),
        str(mode),
        str(out_file),
    ]

    result = subprocess.run(cmd, cwd=workdir)

    return result



# move avg_meshes/jumpingAvg_cage.obj to Dynamic mesh codec for mac v2
shutil.move(f"avg_meshes/{action}Avg_cage.obj", f"Dynamic mesh codec for mac v2/{action}Avg_cage.obj")


exe = f"{workdir}/LaplaceMeshCodec"


run_laplace_avgmesh(
    executable=exe,
    mode="-ea",
    out_file=f"{action}Avg_cage.obj",
    workdir=workdir,
)


# rename Dynamic mesh codec for mac v2/decodedAvgMesh2.obj to avg_meshes/decodedAvgMesh2.obj and Dynamic mesh codec for mac v2/jumpingAvg_cage.obj to avg_meshes/jumpingAvg_cage.obj

shutil.move(f"{workdir}/decodedAvgMesh2.obj", "avg_meshes/decodedAvgMesh2.obj")
shutil.move(f"{workdir}/{action}Avg_cage.obj", f"avg_meshes/{action}Avg_cage.obj")



# rename Dynamic mesh codec for mac v2/map.txt to avg_meshes/jumpingAvg_cage_map.txt
if not os.path.exists(f"avg_meshes/{action}Avg_cage_map.txt"):
    os.rename("Dynamic mesh codec for mac v2/map.txt", "avg_meshes/map.txt")



# read txt file and create a mapping dictionary
def load_mapping_from_txt(file_path):
    mapping = {}
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            mapping[i] = int(line.strip())
    return mapping
 
 
def save_mapping_to_txt(mapping, file_path):
    with open(file_path, "w") as file:
        for key, value in mapping.items():
            file.write(f"{key} {value}\n")



# run EPC_Codec.exe -e <filename.obj> <targe`tfile.bin> 0.01 2
def run_codec_encoder(input_file, output_file, threshold=0.01, parameter=2):
    command = [
        "StaticCoderPerceptual/EPC_codec",
        "-e", input_file,
        output_file,
        str(threshold),
        str(parameter)
    ]
    subprocess.run(command, check=True)



def run_codec_decoder(input_file, output_file, parameter=2):
    command = [
        "StaticCoderPerceptual/EPC_codec",
        "-d", input_file,
        output_file,
        str(parameter)
        ]
    subprocess.run(command, check=True)



input_file = f"avg_meshes/{action}Avg.obj"
avg_string = os.path.basename(input_file).replace('.obj', '')



map_file = f"{avg_string}_map.txt"
new_map_file = os.path.join("avg_meshes", map_file)



x = time.time()
if not os.path.exists(input_file.replace(".obj", ".bin")):
    run_codec_encoder(input_file, input_file.replace(".obj", ".bin"), (parameter_avg_mesh / cage_avg_length))


    # change name and location of "map.txt" to "avg_meshes\{action}Avg_map.txt"

    # map_file = f"{avg_string}_map.txt"
    if os.path.exists("map.txt"):   
        # new_map_file = os.path.join("avg_meshes", map_file)
        os.rename("map.txt", new_map_file)

        mapping = load_mapping_from_txt(new_map_file)
        save_mapping_to_txt(mapping, new_map_file)
y = time.time()

M_bar_dash_enc = y - x

x = time.time()
if not os.path.exists(input_file.replace(".obj", "_decoded.obj")):
    # run the decoder on the bin file
    run_codec_decoder(input_file.replace(".obj", ".bin"), input_file.replace('.obj', '_decoded.obj'))

y = time.time()

e = y - x


if not os.path.exists(input_file.replace('.obj', '_decoded_restructured.obj')):
    # create a remapped cage file
    remapped_mesh = RemappedCageFile(
        cage_file=input_file.replace('.obj', '_decoded.obj'),
        mapping_file=new_map_file
    )
    remapped_mesh.export_remapped_cage()



# save the MVC result to a a folder named coordinates
if not os.path.exists("coordinates"):
    os.makedirs("coordinates")



# if mean value coordinates file already exists, skip computation
mvc_path = os.path.join("coordinates", f"{avg_string}_mvc_compressed.npy")



# rename avg_meshes/decodedAvgMesh2.obj to avg_meshes/jumpingAvg_cage_decoded_restructured.obj

if not os.path.exists(f"avg_meshes/{action}Avg_cage_decoded_restructured.obj"):
    os.rename("avg_meshes/decodedAvgMesh2.obj", f"avg_meshes/{action}Avg_cage_decoded_restructured.obj")



cage_mapping_file = f"avg_meshes/{action}Avg_cage_map.txt"
initial_cage_mapping_file = "avg_meshes/map.txt"
if not os.path.exists(cage_mapping_file):
    cage_mapping = load_mapping_from_txt(initial_cage_mapping_file)
    # cage_mapping

    # save_mapping_to_txt(cage_mapping, cage_mapping_file)


    # reverse cage mapping dictionary
    cage_mapping_reversed = {v: k for k, v in cage_mapping.items()}
    save_mapping_to_txt(cage_mapping_reversed, cage_mapping_file)

input_file_cage = f"avg_meshes/{action}Avg_cage.obj"



if not os.path.exists(input_file_cage.replace('.obj', '_restructured.obj')):
    # create a remapped cage file
    remapped_mesh = RemappedCageFile(
        cage_file=input_file_cage,
        mapping_file=cage_mapping_file
    )
    remapped_mesh.export_remapped_cage()


x = time.time()

print("Computing mean value coordinates...")

if os.path.exists(mvc_path):
    mean_value_compressed = np.load(mvc_path)
else:
    mesh_vertices, mesh_faces = igl.read_triangle_mesh(input_file.replace('.obj', '_decoded_restructured.obj'))
    cage_vertices, cage_faces = igl.read_triangle_mesh(input_file.replace('.obj', '_cage_decoded_restructured.obj'))

    mean_value_compressed = compute_mvc(mesh_vertices, cage_vertices, cage_faces)
    # mean_value_compressed = compute_mvc_matrix(mesh_vertices, cage_vertices, cage_faces)

    # save the mean value coordinates to a file
    mvc_path = os.path.join("coordinates", f"{avg_string}_mvc_compressed.npy")
    np.save(mvc_path, mean_value_compressed)


if not os.path.exists(f"cage_avg/{action}_cage_avg"):
    print("compute cages...")

    input_folder = f"original_meshes/{action}_mesh"
    output_folder = f"cage_avg/{action}_cage_avg"
    # cage = trimesh.load(input_file.replace(".obj", "") + "_cage.obj", force='mesh')
    # cage = trimesh.load(input_file.replace(".obj", "") + "_cage_decoded_restructured.obj", force='mesh')
    cage_vertices, cage_faces = igl.read_triangle_mesh(input_file.replace('.obj', '_cage_decoded_restructured.obj'))
    
    mvc = np.load(mvc_path)
    mvc_inv = np.ascontiguousarray(np.linalg.pinv(mvc))   # 2500 x 10002, once

    # print(os.listdir(input_folder))

    obj_files = sorted(f for f in os.listdir(input_folder) if f.endswith(".obj"))
    meshes = [igl.read_triangle_mesh(os.path.join(input_folder, f))[0]
            for f in obj_files]                          # each 10002 x 3

    big = np.ascontiguousarray(np.hstack(meshes))          # 10002 x (3F)
    out = mvc_inv @ big                                     # one GEMM -> 2500 x (3F)

    os.makedirs(output_folder, exist_ok=True)
    for i, f_i in enumerate(obj_files):
        v = out[:, 3*i:3*i+3]
        new_mesh = trimesh.Trimesh(vertices=v, faces=cage_faces)
        new_obj_path = os.path.join(output_folder, f_i.replace("mesh", "cage"))
        new_mesh.export(new_obj_path, file_type="obj")
        print(f"Transformed {f_i} and saved to {new_obj_path}")

y = time.time()

C_bold_enc = y - x


# change the folder of avg_meshes/bouncingAvg_cage.obj and cage_avg/bouncing_cage_avg to Dynamic mesh codec for mac v2
if not os.path.exists(f"Dynamic mesh codec for mac v2/avg_meshes/{action}Avg_cage_restructured.obj"):
    os.makedirs("Dynamic mesh codec for mac v2/avg_meshes", exist_ok=True)
    shutil.copy(f"avg_meshes/{action}Avg_cage_restructured.obj", f"Dynamic mesh codec for mac v2/avg_meshes/{action}Avg_cage_restructured.obj")

if not os.path.exists(f"Dynamic mesh codec for mac v2/cage_avg/{action}_cage_avg"):
    os.makedirs(f"Dynamic mesh codec for mac v2/cage_avg", exist_ok=True)
    shutil.copytree(f"cage_avg/{action}_cage_avg", f"Dynamic mesh codec for mac v2/cage_avg/{action}_cage_avg")



import shutil
from pathlib import Path
import subprocess, os


def run_laplace_mesh_codec(
    executable: str = "./LaplaceMeshCodec",
    mode: str = "-ed",
    method: str = f"original_meshes/{action}_mesh",
    pattern: str = r"mesh_[0-9]+\.obj",
    out_bin: str = "out.bin",
    alpha: float = 0.9,
    k: int = 4,
    avg_mesh: str = f"Dynamic mesh codec for mac v2/avg_meshes/{action}Avg_cage_decoded_restructured.obj",
    workdir: str | None = None,
) -> subprocess.CompletedProcess:

    exe_path = Path(executable)


    cmd = [
        str(exe_path),
        str(mode),
        str(method),
        str(pattern),
        str(out_bin),
        str(alpha),
        str(int(k)),
        str(avg_mesh),
    ]

    result = subprocess.run(cmd, cwd=workdir)

    return result


exe = f"{workdir}/LaplaceMeshCodec"

x = time.time()

run_laplace_mesh_codec(
    executable=exe,
    mode="-ed",
    method=f"cage_avg/{action}_cage_avg",                  # <-- this is the INPUT FOLDER name
    pattern=r"cage_[0-9]+\.obj",     # files inside ./cage_avg/jumping_cage_avg
    out_bin=f"compressed_{action}.bin",               # will be written in workdir
    alpha=alpha,
    k=4,
    avg_mesh=f"avg_meshes/{action}Avg_cage_restructured.obj",         # lives in workdir (per your tree)
    workdir=workdir,                 # run from the parent that contains ./cage_avg/jumping_cage_avg
)

y = time.time()
C_bin_enc = y - x

alpha_str = str(alpha).replace(".", "_")


def run_laplace_mesh_decodec(
    executable: str = "./LaplaceMeshCodec",
    mode: str = "-dd",
    out_bin: str = f"compressed_{action}.bin",
    decoded: str = f"decompressed_{action}//{alpha_str}//cage_",
    k: int = 4,
    workdir: str | None = None,
) -> subprocess.CompletedProcess:

    exe_path = Path(executable)

    cmd = [
        str(exe_path),
        str(mode),
        str(out_bin),
        str(decoded),
        str(int(k)),
    ]

    result = subprocess.run(cmd, cwd=workdir)

    return result



input_file = f"avg_meshes/{action}Avg.obj"
avg_string = os.path.basename(input_file).replace('.obj', '')


os.makedirs(f"{workdir}/decompressed_{action}_1/{alpha_str}", exist_ok=True)

exe = f"{workdir}/LaplaceMeshCodec"

x = time.time()

run_laplace_mesh_decodec(
    executable=exe,
    mode="-dd",
    decoded=f"decompressed_{action}_1/{alpha_str}/cage_",
    out_bin=f"compressed_{action}.bin",               # will be written in workdir
    k=4,
    workdir=workdir,                 # run from the parent that contains ./samba
)

y = time.time()

C_bold_dash_dec = y - x


        
@njit(cache=True, fastmath=False)
def solve_3x3(A, b):
    M = np.empty((3, 4), dtype=np.float64)
    for i in range(3):
        M[i, 0] = A[i, 0]; M[i, 1] = A[i, 1]; M[i, 2] = A[i, 2]; M[i, 3] = b[i]

    for k in range(3):
        piv = k
        maxabs = abs(M[k, k])
        for r in range(k + 1, 3):
            v = abs(M[r, k])
            if v > maxabs:
                maxabs = v
                piv = r
        if piv != k:
            for j in range(k, 4):
                tmp = M[k, j]; M[k, j] = M[piv, j]; M[piv, j] = tmp

        pivv = M[k, k]
        invp = 1.0 / pivv
        for j in range(k, 4):
            M[k, j] *= invp

        for r in range(3):
            if r == k:
                continue
            factor = M[r, k]
            for j in range(k, 4):
                M[r, j] -= factor * M[k, j]

    x = np.empty(3, dtype=np.float64)
    x[0] = M[0, 3]; x[1] = M[1, 3]; x[2] = M[2, 3]
    return x


@njit(cache=True, fastmath=False)
def refine_vertex_point_newton_method_numba_fast(
    p0_np,
    U_seq_np,
    V_seq_np,
    vertex_i,
    cage_V0_np,
    cage_F_np,
    steps=1,
    alpha=0.0,
    h=1e-9,
    mvc_eps=0.0
):
    p = p0_np.copy()

    m = U_seq_np.shape[0]
    N = U_seq_np.shape[1]

    # ---------------------------------------------------------
    # b = sum_l U_l v_l
    #
    # Instead of passing V_seq_i_np, read vertex_i directly
    # from the complete V_seq_np array.
    # ---------------------------------------------------------
    b = np.zeros(N, dtype=np.float64)

    for l in range(m):
        vx = V_seq_np[l, vertex_i, 0]
        vy = V_seq_np[l, vertex_i, 1]
        vz = V_seq_np[l, vertex_i, 2]

        for n in range(N):
            b[n] += (
                U_seq_np[l, n, 0] * vx +
                U_seq_np[l, n, 1] * vy +
                U_seq_np[l, n, 2] * vz
            )

    # ---------------------------------------------------------
    # Everything below here can remain the same
    # ---------------------------------------------------------

    w     = np.empty(N, dtype=np.float64)
    w_pos = np.empty(N, dtype=np.float64)

    Ehat = np.empty((N, 3), dtype=np.float64)
    En   = np.empty(N, dtype=np.float64)

    Ehat2 = np.empty((N, 3), dtype=np.float64)
    En2   = np.empty(N, dtype=np.float64)

    D    = np.empty((N, 3), dtype=np.float64)
    pred = np.empty((m, 3), dtype=np.float64)
    Aw   = np.empty(N, dtype=np.float64)
    r    = np.empty(N, dtype=np.float64)

    T  = np.empty((m, 3, 3), dtype=np.float64)
    AD = np.empty((N, 3), dtype=np.float64)

    F  = np.empty(3, dtype=np.float64)
    DF = np.empty((3, 3), dtype=np.float64)

    pp = np.empty(3, dtype=np.float64)

    for _ in range(steps):

        # MVC at current point
        mvc_weights_point_numba_out(
            p,
            cage_V0_np,
            cage_F_np,
            w,
            Ehat,
            En,
            mvc_eps
        )

        # -----------------------------------------------------
        # Finite differences
        # -----------------------------------------------------
        invh = 1.0 / h

        for d in range(3):
            pp[0] = p[0]
            pp[1] = p[1]
            pp[2] = p[2]

            pp[d] += h

            mvc_weights_point_numba_out(
                pp,
                cage_V0_np,
                cage_F_np,
                w_pos,
                Ehat2,
                En2,
                mvc_eps
            )

            for n in range(N):
                D[n, d] = (w_pos[n] - w[n]) * invh

        # -----------------------------------------------------
        # pred[l] = U_l^T w
        # -----------------------------------------------------
        for l in range(m):
            s0 = 0.0
            s1 = 0.0
            s2 = 0.0

            for n in range(N):
                wn = w[n]

                s0 += U_seq_np[l, n, 0] * wn
                s1 += U_seq_np[l, n, 1] * wn
                s2 += U_seq_np[l, n, 2] * wn

            pred[l, 0] = s0
            pred[l, 1] = s1
            pred[l, 2] = s2

        # -----------------------------------------------------
        # Aw = sum_l U_l pred[l]
        # -----------------------------------------------------
        for n in range(N):
            s = 0.0

            for l in range(m):
                s += (
                    U_seq_np[l, n, 0] * pred[l, 0] +
                    U_seq_np[l, n, 1] * pred[l, 1] +
                    U_seq_np[l, n, 2] * pred[l, 2]
                )

            Aw[n] = s

        # -----------------------------------------------------
        # r
        # -----------------------------------------------------
        for n in range(N):
            r[n] = Aw[n] - b[n]

        # -----------------------------------------------------
        # F = D^T r
        # -----------------------------------------------------
        for d in range(3):
            s = 0.0

            for n in range(N):
                s += D[n, d] * r[n]

            F[d] = s

        # -----------------------------------------------------
        # T[l] = U_l^T D
        # -----------------------------------------------------
        for l in range(m):
            for c in range(3):
                for d in range(3):

                    s = 0.0

                    for n in range(N):
                        s += U_seq_np[l, n, c] * D[n, d]

                    T[l, c, d] = s

        # -----------------------------------------------------
        # AD
        # -----------------------------------------------------
        for n in range(N):
            for d in range(3):

                s = 0.0

                for l in range(m):
                    s += (
                        U_seq_np[l, n, 0] * T[l, 0, d] +
                        U_seq_np[l, n, 1] * T[l, 1, d] +
                        U_seq_np[l, n, 2] * T[l, 2, d]
                    )

                AD[n, d] = s

        # -----------------------------------------------------
        # DF
        # -----------------------------------------------------
        for i in range(3):
            for j in range(3):

                s = 0.0

                for n in range(N):
                    s += D[n, i] * AD[n, j]

                DF[i, j] = s

        DF[0, 0] += alpha
        DF[1, 1] += alpha
        DF[2, 2] += alpha

        # -----------------------------------------------------
        # Newton update
        # -----------------------------------------------------
        x = solve_3x3(DF, F)

        p[0] -= x[0]
        p[1] -= x[1]
        p[2] -= x[2]

    return p


@njit(parallel=True, cache=True, fastmath=False)
def refine_mesh_parallel(
    mesh_vertices,
    U_seq_np,
    V_seq_np,
    cage_V0_np,
    cage_F_np,
    steps=1,
    alpha=0.0,
    h=1e-9,
    mvc_eps=0.0
):
    num_vertices = mesh_vertices.shape[0]

    refined = np.empty(
        (num_vertices, 3),
        dtype=np.float64
    )

    # ---------------------------------------------------------
    # THIS is the parallel loop
    # ---------------------------------------------------------
    for i in prange(num_vertices):

        p = refine_vertex_point_newton_method_numba_fast(
            mesh_vertices[i],
            U_seq_np,
            V_seq_np,
            i,
            cage_V0_np,
            cage_F_np,
            steps,
            alpha,
            h,
            mvc_eps
        )

        refined[i, 0] = p[0]
        refined[i, 1] = p[1]
        refined[i, 2] = p[2]

    return refined

x = time.time()

# parse through all the .obj files in cage_avg/bouncing_cage_avg and create (m, N, 3) array of cage vertices
# cage_avg_folder = f"cage_avg/{action}_cage_avg"
cage_avg_folder = f"Dynamic mesh codec for mac v2/decompressed_{action}_1/{alpha_str}"
cage_files = sorted([f for f in os.listdir(cage_avg_folder) if f.endswith(".obj")])
cage_vertices_list = []
for cage_file in cage_files:
    cage_path = os.path.join(cage_avg_folder, cage_file)
    cage_V, cage_F = igl.read_triangle_mesh(cage_path)
    cage_vertices_list.append(cage_V)

U_seq_np = np.array(cage_vertices_list, dtype=np.float64)  # (m, N, 3)



# parse through all the .obj files in original_meshes/bouncing_mesh_off and create (m, N, 3) array of original mesh vertices
original_mesh_folder = f"original_meshes/{action}_mesh"
original_mesh_files = sorted([f for f in os.listdir(original_mesh_folder) if f.endswith(".obj")])
original_mesh_vertices_list = []
for original_mesh_file in original_mesh_files:
    original_mesh_path = os.path.join(original_mesh_folder, original_mesh_file)
    original_mesh_V, original_mesh_F = igl.read_triangle_mesh(original_mesh_path)
    original_mesh_vertices_list.append(original_mesh_V)

V_seq_np = np.array(original_mesh_vertices_list, dtype=np.float64)  # (m, N, 3)
# V_seq_np.shape


# input_file.replace('.obj', '_decoded_restructured_old.obj')


mesh_vertices, mesh_faces = igl.read_triangle_mesh(input_file.replace('.obj', '_decoded_restructured.obj'))


cage_vertices, cage_faces = igl.read_triangle_mesh(input_file.replace('.obj', '_cage_decoded_restructured.obj'))


# loop over all vertices and refine them
num_vertices = mesh_vertices.shape[0]
refined_mesh_vertices = np.zeros_like(mesh_vertices, dtype=np.float64)
# loss_per_vertex = np.zeros(num_vertices, dtype=np.float64)

mesh_vertices_c = np.ascontiguousarray(mesh_vertices, dtype=np.float64)
U_seq_c         = np.ascontiguousarray(U_seq_np, dtype=np.float64)
V_seq_c         = np.ascontiguousarray(V_seq_np, dtype=np.float64)
cage_V_c        = np.ascontiguousarray(cage_vertices, dtype=np.float64)
cage_F_c        = np.ascontiguousarray(cage_faces, dtype=np.int32)   # faces int32
refined_mesh_vertices = np.empty_like(mesh_vertices_c)


refined_mesh_vertices = refine_mesh_parallel(
    mesh_vertices_c,
    U_seq_c,
    V_seq_c,
    cage_V_c,
    cage_F_c,
    steps=1,
    alpha=0.0,
    h=1e-9,
)

y = time.time()
# print(f"Refinement took {t2 - t1:.2f} seconds")

M_bar_opt = y - x

recreated_mesh = trimesh.Trimesh(vertices=refined_mesh_vertices, faces=mesh_faces)


# rename avg_meshes/bouncingAvg_decoded_restructured.obj to avg_meshes/bouncingAvg_decoded_restructured_old.obj
if os.path.exists(f"avg_meshes/{action}Avg_decoded_restructured.obj"):
    os.rename(f"avg_meshes/{action}Avg_decoded_restructured.obj", f"avg_meshes/{action}Avg_decoded_restructured_old.obj")

# save recreated mesh as avg_meshes/bouncingAvg_decoded_restructured.obj
recreated_mesh.export(f"avg_meshes/{action}Avg_decoded_restructured_temp.obj", file_type='obj')

x = time.time()

run_codec_encoder(f'avg_meshes/{action}Avg_decoded_restructured_temp.obj', input_file.replace(".obj", "_1.bin"), (parameter_avg_mesh / cage_avg_length))

y = time.time()

M_bin_opt = y - x

# change name and location of "map.txt" to "avg_meshes\{action}Avg_map.txt"

# map_file = f"{avg_string}_map.txt"
if os.path.exists("map.txt"):   
    # new_map_file = os.path.join("avg_meshes", map_file)
    os.rename("map.txt", new_map_file)

    mapping = load_mapping_from_txt(new_map_file)
    save_mapping_to_txt(mapping, new_map_file)

x = time.time()

# run the decoder on the bin file
run_codec_decoder(input_file.replace(".obj", "_1.bin"), input_file.replace('.obj', '_decoded_restructured.obj'))

y = time.time()

M_C_C_bold_bar_dash_dec = C_bold_dash_dec + y - x


# create a remapped cage file
remapped_mesh = RemappedCageFile(
    cage_file=input_file.replace('.obj', '_decoded_restructured.obj'),
    mapping_file=new_map_file
)
remapped_mesh.export_remapped_cage()

# remove avg_meshes/bouncingAvg_decoded_restructured.obj and rename avg_meshes/bouncingAvg_decoded_restructured_restructured.obj as avg_meshes/bouncingAvg_decoded_restructured.obj
if os.path.exists(f"avg_meshes/{action}Avg_decoded_restructured.obj"):
    os.remove(f"avg_meshes/{action}Avg_decoded_restructured.obj")
if os.path.exists(f"avg_meshes/{action}Avg_decoded_restructured_restructured.obj"):
    os.rename(f"avg_meshes/{action}Avg_decoded_restructured_restructured.obj", f"avg_meshes/{action}Avg_decoded_restructured.obj")


# ----------------------------------------------------------------------------------------------
# Recreate meshes from cages using MVC
# ----------------------------------------------------------------------------------------------

input_folder = f"Dynamic mesh codec for mac v2/decompressed_{action}_1/{alpha_str}"
# output_folder = f"decoded_meshes/decompressed_{action}_restructured_mesh/{alpha_str}"
output_folder = f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_mesh_1/{alpha_str}"

x = time.time()

if not os.path.exists(output_folder):
    # mesh = trimesh.load(input_file, force='mesh')
    mesh_vertices, mesh_faces = igl.read_triangle_mesh(input_file)


    mesh_v_avg, mesh_f_avg = igl.read_triangle_mesh(input_file.replace('.obj', '_decoded_restructured.obj'))
    cage_v_avg, cage_f_avg = igl.read_triangle_mesh(input_file.replace('.obj', '_cage_decoded_restructured.obj'))

    mvc = compute_mvc(mesh_v_avg, cage_v_avg, cage_f_avg)

    obj_files = sorted(f for f in os.listdir(input_folder) if f.endswith(".obj"))

    cages = [igl.read_triangle_mesh(os.path.join(input_folder, f))[0]
            for f in obj_files]                      # each K x 3

    big = np.ascontiguousarray(np.hstack(cages))  # K x (3F)
    mvc = np.ascontiguousarray(mvc)              # M x K

    out = mvc @ big                                    # one GEMM -> M x (3F)

    os.makedirs(output_folder, exist_ok=True)
    for i, f_i in enumerate(obj_files):
        v = out[:, 3*i:3*i+3]
        mesh = trimesh.Trimesh(vertices=v, faces=mesh_faces)
        new_path = os.path.join(output_folder, f_i.replace("cage", "mesh").replace("_0", "_"))
        mesh.export(new_path, file_type="obj")

y = time.time()

M_bold_bar_dash_dec = y - x


if not os.path.exists(f"original_meshes/{action}_mesh_off"):
    obj_to_off(f"original_meshes/{action}_mesh", 
               f"original_meshes/{action}_mesh_off")

# move f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_mesh_1/{alpha_str}" to decoded_meshes

shutil.move(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_mesh_1/{alpha_str}", 
                f"decoded_meshes/decompressed_{action}_restructured_mesh_1/{alpha_str}")

if not os.path.exists(f"decoded_meshes/decompressed_{action}_restructured_mesh_off_1/{alpha_str}"):
    obj_to_off(f"decoded_meshes/decompressed_{action}_restructured_mesh_1/{alpha_str}", 
               f"decoded_meshes/decompressed_{action}_restructured_mesh_off_1/{alpha_str}")



# run STED.exe <directory orig> <directory dist>

def run_sted(orig_dir, dist_dir):
    command = [
        "dotnet",
        "STED_for_Mac/STED.dll",
        orig_dir,
        dist_dir
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout




original_dir = f"original_meshes/{action}_mesh_off"
distorted_dir = f"decoded_meshes/decompressed_{action}_restructured_mesh_off_1/{alpha_str}"


sted_result = run_sted(original_dir, distorted_dir)


def extract_sted_value(output):
    lines = output.split('\n')
    for line in lines:
        if 'STED Distortion:' in line:
            return float(line.split(': ')[1])
    return None


sted_r = extract_sted_value(sted_result)



print(f"STED Value for alpha {alpha} is: {sted_r}")


# remove f"avg_meshes/{action}Avg.bin"
if os.path.exists(f"avg_meshes/{action}Avg.bin"):
    os.remove(f"avg_meshes/{action}Avg.bin")
# rename f"avg_meshes/{action}Avg_1.bin" to f"avg_meshes/{action}Avg.bin"
if os.path.exists(f"avg_meshes/{action}Avg_1.bin"):
    os.rename(f"avg_meshes/{action}Avg_1.bin", f"avg_meshes/{action}Avg.bin")

avg_mesh_size = os.path.getsize(f"avg_meshes/{action}Avg.bin")
compressed_mesh_size = os.path.getsize(f"Dynamic mesh codec for mac v2/compressed_{action}.bin")
total_size = avg_mesh_size + compressed_mesh_size
mesh_vertices, mesh_faces = igl.read_triangle_mesh(input_file.replace('.obj', '_decoded_restructured.obj'))
bpvf = total_size * 8 / (mesh_vertices.shape[0] * len(V_seq_np))  # bits per vertex per frame


print(f"STED Value for alpha {alpha} is: {sted_r}")
print(f"BPVF Value for alpha {alpha} is: {bpvf}")


# write sted_result, parameter_coddyac and action in 3 different columns in a csv file
import pandas as pd
def save_sted_result_to_csv(sted_value, parameter, action, bpvf):
    df = pd.DataFrame({
        'Action': [action],
        'Parameter': [parameter],
        'STED Value': [sted_value],
        'bpvf': [bpvf]
    })
    csv_file = f"sted_results_refined/sted_results_mvc_mvc_{action}_{cage_avg_fac.shape[0]}.csv"
    if not os.path.exists("sted_results_refined"):
        os.makedirs("sted_results_refined")
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)


save_sted_result_to_csv(sted_r, alpha, action, bpvf)

def save_run_times(M_bar_dash_enc, C_bold_enc, C_bin_enc, C_bold_dash_dec, M_bar_opt, M_bin_opt, M_C_C_bold_bar_dash_dec, M_bold_bar_dash_dec, action, alpha):
    df = pd.DataFrame({
        'Action': [action],
        'Alpha': [alpha],
        'M_bar_dash_enc': [M_bar_dash_enc],
        'C_bold_enc': [C_bold_enc],
        'C_bin_enc': [C_bin_enc],
        'C_bold_dash_dec': [C_bold_dash_dec],
        'M_bar_opt': [M_bar_opt],
        'M_bin_opt': [M_bin_opt],
        'M_C_C_bold_bar_dash_dec': [M_C_C_bold_bar_dash_dec],
        'M_bold_bar_dash_dec': [M_bold_bar_dash_dec]
    })
    csv_file = f"run_times_refined/run_times_mvc_mvc_{action}_{cage_avg_fac.shape[0]}.csv"
    if not os.path.exists("run_times_refined"):
        os.makedirs("run_times_refined")
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)

save_run_times(M_bar_dash_enc, C_bold_enc, C_bin_enc, C_bold_dash_dec, M_bar_opt, M_bin_opt, M_C_C_bold_bar_dash_dec, M_bold_bar_dash_dec, action, alpha)


# remove folders Dynamic mesh codec for mac v2/avg_meshes and Dynamic mesh codec for mac v2/cage_avg/jumping_cage_avg
shutil.rmtree("Dynamic mesh codec for mac v2/avg_meshes")
shutil.rmtree("Dynamic mesh codec for mac v2/cage_avg")


# move the file compressed_jumping.bin from Dynamic mesh codec for mac v2 to compressed_{action}/{alpha_str}/compressed_jumping.bin by creating the folder if it does not exist
os.makedirs(f"compressed_{action}_1/{alpha_str}", exist_ok=True)
shutil.move(f"Dynamic mesh codec for mac v2/compressed_{action}.bin", f"compressed_{action}_1/{alpha_str}/compressed_{action}.bin")


# remove Dynamic mesh codec for mac v2/decompressed_{jumping}/{alpha_str} 
# shutil.rmtree(f"Dynamic mesh codec for mac v2/decompressed_{action}")

# move f"avg_meshes/{action}Avg_decoded_restructured.obj" to f"avg_meshes/refined_mesh/{alpha_str}/{action}Avg_decoded_restructured.obj"
os.makedirs(f"avg_meshes/refined_mesh/{alpha_str}", exist_ok=True)
shutil.move(f"avg_meshes/{action}Avg_decoded_restructured.obj", f"avg_meshes/refined_mesh/{alpha_str}/{action}Avg_decoded_restructured.obj")

os.rename(f"avg_meshes/{action}Avg_decoded_restructured_old.obj", f"avg_meshes/{action}Avg_decoded_restructured.obj")

# remove f"avg_meshes/{action}Avg_decoded_restructured_temp.obj"
if os.path.exists(f"avg_meshes/{action}Avg_decoded_restructured_temp.obj"):
    os.remove(f"avg_meshes/{action}Avg_decoded_restructured_temp.obj")


# remove Dynamic mesh codec for mac v2/decodedAvgMesh.obj, Dynamic mesh codec for mac v2/decodedAvgMesh2.obj, Dynamic mesh codec for mac v2/temp.bin, Dynamic mesh codec for mac v2/map.txt
if os.path.exists(f"Dynamic mesh codec for mac v2/decodedAvgMesh.obj"):
    os.remove(f"Dynamic mesh codec for mac v2/decodedAvgMesh.obj")
if os.path.exists(f"Dynamic mesh codec for mac v2/decodedAvgMesh2.obj"):
    os.remove(f"Dynamic mesh codec for mac v2/decodedAvgMesh2.obj")
if os.path.exists(f"Dynamic mesh codec for mac v2/temp.bin"):
    os.remove(f"Dynamic mesh codec for mac v2/temp.bin")
if os.path.exists(f"Dynamic mesh codec for mac v2/map.txt"):
    os.remove(f"Dynamic mesh codec for mac v2/map.txt")