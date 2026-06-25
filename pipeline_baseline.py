import subprocess
import os
import numpy as np
from utils_numba import compute_mvc

import igl

from utils_1 import RemappedCageFile, obj_to_off
from utils_2 import RemappedCageFolder, average_edge_length

import shutil
from pathlib import Path
import subprocess, os

import time



wd = os.getcwd()

action = "jumping"  # Change this to the desired action
alpha = 0.25 # This can be adjusted as needed


mesh_avg_vert, mesh_avg_fac = igl.read_triangle_mesh(f"avg_meshes/{action}Avg.obj")
# cage_avg_vert, cage_avg_fac = igl.read_triangle_mesh(f"avg_meshes/{action}Avg_cage.obj")


mesh_avg_length = average_edge_length(mesh_avg_vert, mesh_avg_fac)
# cage_avg_length = average_edge_length(cage_avg_vert, cage_avg_fac)


# move avg_meshes/jumpingAvg.obj to Dynamic mesh codec for mac v2
if not os.path.exists("Dynamic mesh codec for mac v2/avg_meshes"):
    os.makedirs("Dynamic mesh codec for mac v2/avg_meshes")
shutil.move(f"avg_meshes/{action}Avg.obj", f"Dynamic mesh codec for mac v2/avg_meshes/{action}Avg.obj")


input_file = f"avg_meshes/{action}Avg.obj"
avg_string = os.path.basename(input_file).replace('.obj', '')


if not os.path.exists(f"Dynamic mesh codec for mac v2/original_meshes/{action}_mesh"):
    os.makedirs(f"Dynamic mesh codec for mac v2/original_meshes", exist_ok=True)
    shutil.copytree(f"original_meshes/{action}_mesh", f"Dynamic mesh codec for mac v2/original_meshes/{action}_mesh")


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
    avg_mesh: str = f"Dynamic mesh codec for mac v2/{action}Avg.obj",
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



workdir = f"{wd}/Dynamic mesh codec for mac v2"
exe = f"{workdir}/LaplaceMeshCodec"

x = time.time()

run_laplace_mesh_codec(
    executable=exe,
    mode="-ed",
    method=f"original_meshes/{action}_mesh",                  # <-- this is the INPUT FOLDER name
    pattern=r"mesh_[0-9]+\.obj",     # files inside ./original_meshes/jumping_mesh
    out_bin=f"compressed_{action}.bin",               # will be written in workdir
    alpha=alpha,
    k=4,
    avg_mesh=f"avg_meshes/{action}Avg.obj",         # lives in workdir (per your tree)
    # avg_mesh=f"Dynamic mesh codec for mac v2/decodedAvgMesh.obj",         # lives in workdir (per your tree)
    workdir=workdir,                 # run from the parent that contains ./cage_avg/jumping_cage_avg
)

y = time.time()

a = y - x

alpha_str = str(alpha).replace(".", "_")


import shutil
from pathlib import Path
import subprocess, os

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

# parse through all the .obj files in original_meshes/bouncing_mesh_off and create (m, N, 3) array of original mesh vertices
original_mesh_folder = f"original_meshes/{action}_mesh"
original_mesh_files = sorted([f for f in os.listdir(original_mesh_folder) if f.endswith(".obj")])
original_mesh_vertices_list = []
for original_mesh_file in original_mesh_files:
    original_mesh_path = os.path.join(original_mesh_folder, original_mesh_file)
    original_mesh_V, original_mesh_F = igl.read_triangle_mesh(original_mesh_path)
    original_mesh_vertices_list.append(original_mesh_V)

V_seq_np = np.array(original_mesh_vertices_list, dtype=np.float64)  # (m, N, 3)


# make a folder decompressed_jumping in Dynamic mesh codec for mac v2
os.makedirs(f"{workdir}/decompressed_{action}_p2/{alpha_str}", exist_ok=True)


# workdir = "/Users/navdeepsinghbedi/mesh_compression_laplacian/Dynamic mesh codec for mac v2"
exe = f"{workdir}/LaplaceMeshCodec"

x = time.time()

run_laplace_mesh_decodec(
    executable=exe,
    mode="-dd",
    decoded=f"decompressed_{action}_p2/{alpha_str}/mesh_",
    out_bin=f"compressed_{action}.bin",               # will be written in workdir
    k=4,
    workdir=workdir,                 # run from the parent that contains ./samba
)

y = time.time()

b = y - x

# parse decompressed_jumping/0_25/ and remove the leading 0 in the mesh name (mesh_00000.obj -> mesh_0000.obj)
decompressed_folder = f"{workdir}/decompressed_{action}_p2/{alpha_str}"
for filename in os.listdir(decompressed_folder):
    # print(filename[6:])
    if filename.startswith("mesh_"):
        new_filename = "mesh_" + filename[6:]  # remove the leading 0
        # print(f"Renaming {filename} to {new_filename}")
        os.rename(
            os.path.join(decompressed_folder, filename),
            os.path.join(decompressed_folder, new_filename),
        )



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

# move Dynamic mesh codec for mac v2/map.txt to avg_meshes/jumpingAvg_map.txt
shutil.move(f"Dynamic mesh codec for mac v2/map.txt", f"avg_meshes/{action}Avg_map.txt")


cage_mapping_file = f"avg_meshes/{action}Avg_map.txt"
cage_mapping = load_mapping_from_txt(cage_mapping_file)
    # cage_mapping

save_mapping_to_txt(cage_mapping, cage_mapping_file)


if not os.path.exists(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_off_p2/{alpha_str}"):

    remapped_cage = RemappedCageFolder(
    cage_folder=f"Dynamic mesh codec for mac v2/decompressed_{action}_p2/{alpha_str}",
    mapping_file=f"avg_meshes/{action}Avg_map.txt", action=action)

    remapped_cage.export_remapped_cage()

# rename f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_off_p2" to f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2"
shutil.move(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_off_p2", f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2")


if not os.path.exists(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2_off/{alpha_str}"):
    obj_to_off(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2/{alpha_str}", 
               f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2_off/{alpha_str}")




# if not os.path.exists(f"Dynamic mesh codec for mac v2/decompressed_{action}_p2_off/{alpha_str}"):
#     obj_to_off(f"Dynamic mesh codec for mac v2/decompressed_{action}_p2/{alpha_str}", 
#                f"Dynamic mesh codec for mac v2/decompressed_{action}_p2_off/{alpha_str}")



# move Dynamic mesh codec for mac v2/decompressed_{action}_p2/{alpha_str} and Dynamic mesh codec for mac v2/decompressed_{action}_p2_off/{alpha_str} to decoded_meshes
# shutil.move(f"Dynamic mesh codec for mac v2/decompressed_{action}_p2/{alpha_str}", f"decoded_meshes/decompressed_{action}_p2/{alpha_str}")
# shutil.move(f"Dynamic mesh codec for mac v2/decompressed_{action}_p2_off/{alpha_str}", f"decoded_meshes/decompressed_{action}_p2_off/{alpha_str}")

shutil.move(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2/{alpha_str}", f"decoded_meshes/decompressed_{action}_p2/{alpha_str}")
shutil.move(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2_off/{alpha_str}", f"decoded_meshes/decompressed_{action}_p2_off/{alpha_str}")

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
distorted_dir = f"decoded_meshes/decompressed_{action}_p2_off/{alpha_str}"



sted_result = run_sted(original_dir, distorted_dir)


def extract_sted_value(output):
    lines = output.split('\n')
    for line in lines:
        if 'STED Distortion:' in line:
            return float(line.split(': ')[1])
    return None


sted_r = extract_sted_value(sted_result)

compressed_mesh_size = os.path.getsize(f"Dynamic mesh codec for mac v2/compressed_{action}.bin")
# bpvf = compressed_mesh_size * 8 / (mesh_avg_vert.shape[0] * 204)  # bits per vertex per frame
bpvf = compressed_mesh_size * 8 / (mesh_avg_vert.shape[0] * len(V_seq_np))

print(f"STED for action {action} at alpha {alpha}: {sted_r}")
print(f"BPVF for action {action} at alpha {alpha}: {bpvf}")


# write sted_result, parameter_coddyac and action in 3 different columns in a csv file
import pandas as pd
def save_sted_result_to_csv(sted_value, parameter, action, bpvf):
    df = pd.DataFrame({
        'Action': [action],
        'Parameter': [parameter],
        'STED Value': [sted_value],
        'bpvf': [bpvf]
    })
    csv_file = f"sted_results_baseline/sted_results_mvc_mvc_{action}_p2.csv"
    if not os.path.exists("sted_results_baseline"):
        os.makedirs("sted_results_baseline")
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)


save_sted_result_to_csv(sted_r, alpha, action, bpvf)


def save_run_times(a, b, action, alpha):
    df = pd.DataFrame({
        'Action': [action],
        'Alpha': [alpha],
        'a': [a],
        'b': [b],

    })
    csv_file = f"run_times_refined/run_times_mvc_mvc_{action}_p2.csv"
    if not os.path.exists("run_times_refined"):
        os.makedirs("run_times_refined")
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)

save_run_times(a, b, action, alpha)
    


# move Dynamic mesh codec for mac v2/avg_meshes/jumpingAvg.obj back to avg_meshes/
shutil.move(f"Dynamic mesh codec for mac v2/avg_meshes/{action}Avg.obj", f"avg_meshes/{action}Avg.obj")
# remove Dynamic mesh codec for mac v2/avg_meshes/ folder if it is empty
if not os.listdir("Dynamic mesh codec for mac v2/avg_meshes/"):
    os.rmdir("Dynamic mesh codec for mac v2/avg_meshes/")

# move the file compressed_cow.bin from Dynamic mesh codec for mac v2 to compressed_cow_p2/{alpha_str}/compressed_cow.bin by creating the folder if it does not exist
os.makedirs(f"compressed_{action}_p2/{alpha_str}", exist_ok=True)
shutil.move(f"Dynamic mesh codec for mac v2/compressed_{action}.bin", f"compressed_{action}_p2/{alpha_str}/compressed_{action}.bin")

# remove Dynamic mesh codec for mac v2/decodedAvgMesh.obj, Dynamic mesh codec for mac v2/decodedAvgMesh2.obj, Dynamic mesh codec for mac v2/temp.bin, Dynamic mesh codec for mac v2/map.txt
if os.path.exists(f"Dynamic mesh codec for mac v2/decodedAvgMesh.obj"):
    os.remove(f"Dynamic mesh codec for mac v2/decodedAvgMesh.obj")
if os.path.exists(f"Dynamic mesh codec for mac v2/decodedAvgMesh2.obj"):
    os.remove(f"Dynamic mesh codec for mac v2/decodedAvgMesh2.obj")
if os.path.exists(f"Dynamic mesh codec for mac v2/temp.bin"):
    os.remove(f"Dynamic mesh codec for mac v2/temp.bin")
# if os.path.exists(f"Dynamic mesh codec for mac v2/map.txt"):
#     os.remove(f"Dynamic mesh codec for mac v2/map.txt")

# remove Dynamic mesh codec for mac v2/decompressed_jumping_restructured_p2 and Dynamic mesh codec for mac v2/decompressed_jumping_restructured_p2_off
shutil.rmtree(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2")
shutil.rmtree(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_p2_off")