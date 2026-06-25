import os
import trimesh
import numpy as np




# RemappedCage class for off files
 
class RemappedCageFolder:
    def __init__(self, cage_folder, mapping_file, action):
        self.cage_folder = cage_folder
        self.mapping_file = mapping_file
        self.mapping = self.load_mapping()
        self.inverted_mapping = {v: k for k, v in self.mapping.items()}
        self.remapped_faces = None
        self.action = action
 
    # load the cage vertices and faces from .off file
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
        # vertices = self.reorder_cage()
        # faces = self.remap_faces()
 
        # loop through all .off files in the input folder
        for filename in os.listdir(self.cage_folder):
            if filename.endswith(".obj") or filename.endswith(".off"):
                off_path = os.path.join(self.cage_folder, filename)
                vertices, faces = self.load_cage(cage_file=off_path)
                reordered_vertices = self.reorder_cage(vertices=vertices)
 
                # if remapping is needed, remap the faces
                if self.remapped_faces is None:
                    self.remapped_faces = self.remap_faces(faces=faces)
 
       
                # Create a new mesh with the remapped vertices and faces
                remapped_mesh = trimesh.Trimesh(vertices=reordered_vertices, faces=self.remapped_faces)
                output_file = os.path.join(os.path.dirname(off_path).replace(f"{self.action}", f"{self.action}_restructured_off"), filename)
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                if filename.endswith(".obj"):
                    remapped_mesh.export(output_file, file_type='obj')
                else:
                    remapped_mesh.export(output_file, file_type='off')
                print(f"{os.path.join(os.path.dirname(off_path), filename)} to {output_file}")


# function to calculate average edge length of a mesh
def average_edge_length(V, F):
    e1 = V[F[:, 1], :] - V[F[:, 0], :]
    e2 = V[F[:, 2], :] - V[F[:, 1], :]
    e3 = V[F[:, 0], :] - V[F[:, 2], :]
    edge_lengths = np.sqrt(np.sum(e1**2, axis=1)) + np.sqrt(np.sum(e2**2, axis=1)) + np.sqrt(np.sum(e3**2, axis=1))
    return np.mean(edge_lengths) / 3.0


def file_numbering_mesh(input_folder, output_folder, offset):
    os.makedirs(output_folder, exist_ok=True)
   
    for filename in os.listdir(input_folder):
        if filename.startswith("mesh_") and filename.endswith(".obj"):
            try:
                index_str = filename[5:-4]  # "0000" from "mesh_0000.off"
                index = int(index_str)
                new_index = index + offset
                new_filename = f"mesh_{new_index:04d}.obj"  # "mesh_0001.obj"
               
                old_path = os.path.join(input_folder, filename)
                new_path = os.path.join(output_folder, new_filename)
               
                os.rename(old_path, new_path)
                print(f"Renamed {filename} → {new_filename}")
            except ValueError:
                print(f"Skipping {filename}: invalid format")