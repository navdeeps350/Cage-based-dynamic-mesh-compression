import os
import trimesh
import numpy as np


class RemappedCageFile:
    def __init__(self, cage_file, mapping_file):
        self.cage_file = cage_file
        self.mapping_file = mapping_file
        self.mapping = self.load_mapping()
        self.inverted_mapping = {v: k for k, v in self.mapping.items()}
 
    def load_cage(self, cage_file=None):
        mesh = trimesh.load(cage_file, force='mesh')
        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError(f"{cage_file} is not a valid mesh")
        return mesh.vertices, mesh.faces
 
    # load the mapping from the file
    def load_mapping(self):
        mapping = {}
        with open(self.mapping_file, "r") as file:
            for line in file:
                key, value = map(int, line.strip().split())
                mapping[key] = value
        return mapping
    
    # reorder cage vertices
    def reorder_cage(self, vertices=None):
        reordered_vertices = np.array([vertices[self.mapping[i]] for i in range(len(vertices))])
        return reordered_vertices
    
    # remap cage faces
    def remap_faces(self, faces=None):
        for i in range(len(faces)):
            for j in range(len(faces[i])):
                faces[i][j] = self.inverted_mapping[faces[i][j]]
        return faces
    
    def export_remapped_cage(self):
 
        vertices, faces = self.load_cage(cage_file=self.cage_file)
        reordered_vertices = self.reorder_cage(vertices=vertices)
 
        # remap the faces
        remapped_faces = self.remap_faces(faces=faces)
 
        # Create a new mesh with the remapped vertices and faces
        remapped_mesh = trimesh.Trimesh(vertices=reordered_vertices, faces=remapped_faces)
        output_file = os.path.splitext(self.cage_file)[0] + "_restructured.obj"
        remapped_mesh.export(output_file, file_type='obj')
        print(f"Remapped cage exported to {output_file}")



def obj_to_off(input_folder, output_folder):
    """
    Convert all .obj files in the input folder to .off format and save them in the output folder.
    
    Parameters:
    - input_folder: str, path to the folder containing .obj files
    - output_folder: str, path to the folder where .off files will be saved
    """
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".obj"):
            obj_path = os.path.join(input_folder, filename)
            mesh = trimesh.load(obj_path, force='mesh')
            
            if not isinstance(mesh, trimesh.Trimesh):
                print(f"Skipping {filename}: not a valid mesh")
                continue
            
            off_filename = os.path.splitext(filename)[0] + ".off"
            off_path = os.path.join(output_folder, off_filename)
            
            mesh.export(off_path)
            print(f"Converted {filename} → {off_filename}")

def off_to_obj(input_folder, output_folder):
    """
    Convert all .off files in the input folder to .obj format and save them in the output folder.
    
    Parameters:
    - input_folder: str, path to the folder containing .off files
    - output_folder: str, path to the folder where .obj files will be saved
    """
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".off"):
            off_path = os.path.join(input_folder, filename)
            mesh = trimesh.load(off_path, force='mesh')
            
            if not isinstance(mesh, trimesh.Trimesh):
                print(f"Skipping {filename}: not a valid mesh")
                continue
            
            obj_filename = os.path.splitext(filename)[0] + ".obj"
            obj_path = os.path.join(output_folder, obj_filename)
            
            mesh.export(obj_path)
            print(f"Converted {filename} → {obj_filename}")

 
 
def file_numbering(input_folder, output_folder, offset, object_prefix="cage"):
    os.makedirs(output_folder, exist_ok=True)
   
    for filename in os.listdir(input_folder):
        if filename.startswith(object_prefix + "_") and (filename.endswith(".obj") or filename.endswith(".off")):
            try:
                index_str = filename[len(object_prefix) + 1:-4]  # "0000" from "mesh_0000.off"
                index = int(index_str)
                new_index = index + offset
                if filename.endswith(".obj"):
                    extension = ".obj"
                else:                    
                    extension = ".off"
                new_filename = f"{object_prefix}_{new_index:04d}{extension}"  # "mesh_0001.obj" or "mesh_0001.off"

                old_path = os.path.join(input_folder, filename)
                new_path = os.path.join(output_folder, new_filename)
               
                os.rename(old_path, new_path)
                print(f"Renamed {filename} → {new_filename}")
            except ValueError:
                print(f"Skipping {filename}: invalid format")


# change all the file name in the input forlder from, for example "mesh__0000.obj to "mesh_0000.obj"

def fix_file_naming(input_folder, object_prefix="mesh"):
    for filename in os.listdir(input_folder):
        if filename.startswith(object_prefix + "__") and (filename.endswith(".obj") or filename.endswith(".off")):
            new_filename = filename.replace("__", "_", 1)  # Replace only the first occurrence
            old_path = os.path.join(input_folder, filename)
            new_path = os.path.join(input_folder, new_filename)
            os.rename(old_path, new_path)
            print(f"Renamed {filename} → {new_filename}")


# change all the file name in the input forlder from, for example "torus_0000.obj to "mesh_0000.obj"

def rename_files(input_folder, old_prefix, new_prefix):
    for filename in os.listdir(input_folder):
        if filename.startswith(old_prefix + "_") and (filename.endswith(".obj") or filename.endswith(".off")):
            new_filename = filename.replace(old_prefix, new_prefix, 1)  # Replace only the first occurrence
            old_path = os.path.join(input_folder, filename)
            new_path = os.path.join(input_folder, new_filename)
            os.rename(old_path, new_path)
            print(f"Renamed {filename} → {new_filename}")