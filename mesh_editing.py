import os
import trimesh
import numpy as np
from utils_numba import compute_mvc

import igl



action = "jumping"  # Change this to the desired action


mesh_vertices_original, mesh_faces_original = igl.read_triangle_mesh("avg_meshes/jumpingAvg_original.obj")
cage_vertices_original, cage_faces_original = igl.read_triangle_mesh("avg_meshes/jumpingAvg_cage.obj")


mvc = compute_mvc(mesh_vertices_original, cage_vertices_original, cage_faces_original)


input_folder = f"original_meshes/{action}_mesh"
output_folder = f"cage_avg/{action}_cage_avg"
 
mvc_inv = np.linalg.pinv(mvc)

for filename in os.listdir(input_folder):
    if filename.endswith(".obj"):
        # print(filename, mvc.shape, cage.vertices.shape)
        obj_path = os.path.join(input_folder, filename)
        # replace the word "cage" with "mesh" in the filename "dataset_off/decoded/handstand_restructured_obj/cage_0160.obj"
        # mesh = trimesh.load(obj_path, force='mesh')
        mesh_vertices, mesh_faces = igl.read_triangle_mesh(obj_path)
        # new_vertices = mvc_inv @ mesh.vertices
        new_vertices = mvc_inv @ mesh_vertices
        # print(new_vertices.shape)
        # new_mesh = trimesh.Trimesh(vertices=new_vertices, faces=cage.faces)
        new_mesh = trimesh.Trimesh(vertices=new_vertices, faces=cage_faces_original)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        new_obj_path = os.path.join(output_folder, filename.replace("mesh", "cage"))
        new_mesh.export(new_obj_path, file_type='obj')
        print(f"Transformed {filename} and saved to {new_obj_path}")



mesh_vertices_modified, mesh_faces_modified = igl.read_triangle_mesh("avg_meshes/jumpingAvg_modified.obj")


mvc_modified = compute_mvc(mesh_vertices_modified, cage_vertices_original, cage_faces_original)


input_folder = f"cage_avg/{action}_cage_avg"
output_folder = f"mesh_avg/{action}_mesh_modified"

for filename in os.listdir(input_folder):
    if filename.endswith(".obj"):
        obj_path = os.path.join(input_folder, filename)
        cage_vertices, cage_faces = igl.read_triangle_mesh(obj_path)
        new_vertices = mvc_modified @ cage_vertices
        new_mesh = trimesh.Trimesh(vertices=new_vertices, faces=mesh_faces_modified)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        new_obj_path = os.path.join(output_folder, filename.replace("cage", "mesh"))
        new_mesh.export(new_obj_path, file_type='obj')
        print(f"Transformed {filename} and saved to {new_obj_path}")
