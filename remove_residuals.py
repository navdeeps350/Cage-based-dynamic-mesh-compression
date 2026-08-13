import os
import shutil


action = "bouncing"


# for pipeline_ours.py
if os.path.exists(f"Dynamic mesh codec for mac v2/decompressed_{action}_1"):
    shutil.rmtree(f"Dynamic mesh codec for mac v2/decompressed_{action}_1")
if os.path.exists(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_mesh_1"):
    shutil.rmtree(f"Dynamic mesh codec for mac v2/decompressed_{action}_restructured_mesh_1")
if os.path.exists(f"compressed_{action}_1"):
    shutil.rmtree(f"compressed_{action}_1")
if os.path.exists(f"avg_meshes/refined_mesh"):
    shutil.rmtree(f"avg_meshes/refined_mesh")
if os.path.exists(f"avg_meshes/decodedAvgMesh2.obj"):
    os.remove(f"avg_meshes/decodedAvgMesh2.obj")
if os.path.exists(f"avg_meshes/{action}Avg_cage_decoded_restructured.obj"):
    os.remove(f"avg_meshes/{action}Avg_cage_decoded_restructured.obj")
if os.path.exists(f"avg_meshes/{action}Avg_cage_map.txt"):
    os.remove(f"avg_meshes/{action}Avg_cage_map.txt")
if os.path.exists(f"avg_meshes/{action}Avg_cage_restructured.obj"):
    os.remove(f"avg_meshes/{action}Avg_cage_restructured.obj")
if os.path.exists(f"avg_meshes/{action}Avg_decoded_restructured.obj"):
    os.remove(f"avg_meshes/{action}Avg_decoded_restructured.obj")
if os.path.exists(f"avg_meshes/{action}Avg_decoded.obj"):
    os.remove(f"avg_meshes/{action}Avg_decoded.obj")
if os.path.exists(f"avg_meshes/{action}Avg_map.txt"):
    os.remove(f"avg_meshes/{action}Avg_map.txt")
if os.path.exists(f"avg_meshes/{action}Avg.bin"):
    os.remove(f"avg_meshes/{action}Avg.bin")
if os.path.exists(f"avg_meshes/map.txt"):
    os.remove(f"avg_meshes/map.txt")


# for pipeline_baseline.py
if os.path.exists(f"compressed_{action}_p2"):
    shutil.rmtree(f"compressed_{action}_p2")
if os.path.exists(f"Dynamic mesh codec for mac v2/decompressed_{action}_p2"):
    shutil.rmtree(f"Dynamic mesh codec for mac v2/decompressed_{action}_p2")
if os.path.exists(f"Dynamic mesh codec for mac v2/original_meshes"):
    shutil.rmtree(f"Dynamic mesh codec for mac v2/original_meshes")
if os.path.exists(f"avg_meshes/{action}Avg_map.txt"):
    os.remove(f"avg_meshes/{action}Avg_map.txt")