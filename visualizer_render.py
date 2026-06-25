import os
import re
import glob
import numpy as np
import trimesh
import pyrender
import imageio.v2 as imageio


# ###################################### #
# for 1 sequence with captions #
# ###################################### #


# # -------- settings --------
# obj_dir = "sted_results/colored_meshes_opt"
# out_video = "mesh_sequence_final.mp4"
# fps = 24
# width, height = 1280, 720
# bg_color = [255, 255, 255, 255]   # white background
# # --------------------------

# def natural_key(s):
#     return [int(t) if t.isdigit() else t.lower()
#             for t in re.split(r'(\d+)', s)]

# obj_files = sorted(glob.glob(os.path.join(obj_dir, "*.obj")), key=natural_key)
# assert len(obj_files) > 0, "No .obj files found."

# # Compute a global bounding box so camera stays stable across frames
# mins = []
# maxs = []
# for f in obj_files:
#     mesh = trimesh.load(f, force='mesh')
#     mins.append(mesh.bounds[0])
#     maxs.append(mesh.bounds[1])

# global_min = np.min(np.array(mins), axis=0)
# global_max = np.max(np.array(maxs), axis=0)
# center = (global_min + global_max) / 2.0
# extent = np.max(global_max - global_min)

# # Create renderer
# r = pyrender.OffscreenRenderer(viewport_width=width, viewport_height=height)

# writer = imageio.get_writer(out_video, fps=fps)

# for f in obj_files:
#     tri_mesh = trimesh.load(f, force='mesh')

#     # Center and scale mesh consistently
#     tri_mesh.vertices = (tri_mesh.vertices - center) / extent

#     # Convert to pyrender mesh
#     render_mesh = pyrender.Mesh.from_trimesh(tri_mesh, smooth=False)

#     scene = pyrender.Scene(bg_color=bg_color, ambient_light=[0.2, 0.2, 0.2])
#     scene.add(render_mesh)

#     # Camera
#     camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)

#     cam_pose = np.array([
#         [1.0, 0.0, 0.0,  0.0],
#         [0.0, 1.0, 0.0,  0.2],
#         [0.0, 0.0, 1.0,  2.5],
#         [0.0, 0.0, 0.0,  1.0]
#     ])
#     scene.add(camera, pose=cam_pose)

#     # Light
#     light = pyrender.DirectionalLight(color=np.ones(3), intensity=1.0)
#     scene.add(light, pose=cam_pose)

#     color, _ = r.render(scene)
#     writer.append_data(color)

# writer.close()
# # r.delete()

# print(f"Saved video to: {out_video}")



# ###################################### #
# for 2 sequences side-by-side with captions #
# ###################################### #


import os
import re
import glob
import numpy as np
import trimesh
import pyrender
import imageio.v2 as imageio
from PIL import Image, ImageDraw, ImageFont

# -------- settings --------
obj_dir_a   = "jumping_original_modified/jumping_mesh"   # first sequence folder
obj_dir_b   = "jumping_original_modified/mesh_avg/jumping_mesh_modified"  # second sequence folder
caption_a   = "Original mesh sequence"
caption_b   = "Modified mesh sequence"
out_video   = "mesh_sequence.mp4"
fps         = 14
panel_w, panel_h = 1280, 1280          # size of each rendered panel
caption_h   = 48                     # pixel height reserved for captions
bg_color    = [255, 255, 255, 255]   # white background
font_size   = 28
# --------------------------

def natural_key(s):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r'(\d+)', s)]

def get_obj_files(folder):
    files = sorted(glob.glob(os.path.join(folder, "*.obj")), key=natural_key)
    assert len(files) > 0, f"No .obj files found in {folder}"
    return files

def compute_global_bounds(obj_files):
    mins, maxs = [], []
    for f in obj_files:
        mesh = trimesh.load(f, force='mesh')
        mins.append(mesh.bounds[0])
        maxs.append(mesh.bounds[1])
    g_min = np.min(np.array(mins), axis=0)
    g_max = np.max(np.array(maxs), axis=0)
    center = (g_min + g_max) / 2.0
    extent = np.max(g_max - g_min)
    return center, extent

def look_at_pose(eye, target=np.array([0,0,0]), up=np.array([0,1,0])):
    """Build a pyrender camera pose looking from `eye` toward `target`."""
    eye = np.array(eye, dtype=float)
    forward = target - eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, forward)
    pose = np.eye(4)
    pose[:3, 0] = right
    pose[:3, 1] = true_up
    pose[:3, 2] = -forward   # camera looks in its -Z
    pose[:3, 3] = eye
    return pose

def render_frame(renderer, obj_path, center, extent):
    """Render one .obj file and return an H×W×3 numpy array."""
    tri_mesh = trimesh.load(obj_path, force='mesh')
    tri_mesh.vertices = (tri_mesh.vertices - center) / extent

    render_mesh = pyrender.Mesh.from_trimesh(tri_mesh, smooth=False)

    # Subtle ambient so shadows stay dark; strong directional for contrast
    scene = pyrender.Scene(bg_color=bg_color, ambient_light=[0.05, 0.05, 0.05])
    scene.add(render_mesh)

    camera = pyrender.PerspectiveCamera(yfov=np.pi / 4.0)
    # cam_pose = np.array([
    #     [1.0, 0.0, 0.0,  0.0],
    #     [0.0, 1.0, 0.0,  0.2],
    #     [0.0, 0.0, 1.0,  2.5],
    #     [0.0, 0.0, 0.0,  1.0],
    # ])

    # cam_pose = np.array([
    #     [1.0, 0.0, 0.0,  0.0],
    #     [0.0, 1.0, 0.0,  0.1],
    #     [0.0, 0.0, 1.0,  1.6],   # closer than before (was 2.5)
    #     [0.0, 0.0, 0.0,  1.0],
    # ])

    # cam_pose = look_at_pose(eye=[0, 0.1, -1.6])   # current front view
    cam_pose = look_at_pose(eye=[1.6, 0.1, 0])


    scene.add(camera, pose=cam_pose)

    # Key light — bright, from camera direction
    # key_light = pyrender.DirectionalLight(color=np.ones(3), intensity=6.0)
    # scene.add(key_light, pose=cam_pose)

    # Fill light — softer, from upper-left
    fill_pose = np.array([
        [ 0.866, 0.0,  0.5,  -1.0],
        [ 0.0,   1.0,  0.0,   0.5],
        [-0.5,   0.0,  0.866, 2.0],
        [ 0.0,   0.0,  0.0,   1.0],
    ])
    fill_light = pyrender.DirectionalLight(color=np.ones(3), intensity=2.0)
    scene.add(fill_light, pose=fill_pose)

    color, _ = renderer.render(scene)
    return color  # H×W×3 uint8

def add_caption_bar(frames_a_b, cap_a, cap_b, panel_w, panel_h, caption_h, font_size):
    """
    Composites two rendered panels side-by-side and adds captions.
    Returns a list of H×W×3 numpy arrays ready for the video writer.
    """
    total_w = panel_w * 2
    total_h = panel_h + caption_h

    # Try to load a clean font; fall back to default if unavailable
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except Exception:
            font = ImageFont.load_default()

    out_frames = []
    for img_a, img_b in frames_a_b:
        canvas = Image.new("RGB", (total_w, total_h), color=(255, 255, 255))

        # Paste rendered panels
        canvas.paste(Image.fromarray(img_a), (0, 0))
        canvas.paste(Image.fromarray(img_b), (panel_w, 0))

        draw = ImageDraw.Draw(canvas)

        # Divider line between panels
        draw.line([(panel_w, 0), (panel_w, total_h)], fill=(180, 180, 180), width=2)

        # Captions — centered under each panel
        for caption, x_offset in [(cap_a, 0), (cap_b, panel_w)]:
            bbox = draw.textbbox((0, 0), caption, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            tx = x_offset + (panel_w - text_w) // 2
            ty = panel_h + (caption_h - text_h) // 2
            # Subtle shadow for readability
            draw.text((tx + 1, ty + 1), caption, font=font, fill=(180, 180, 180))
            draw.text((tx, ty), caption, font=font, fill=(30, 30, 30))

        out_frames.append(np.array(canvas))

    return out_frames


# ---------- main ----------

files_a = get_obj_files(obj_dir_a)
files_b = get_obj_files(obj_dir_b)

# Align sequence lengths (use the shorter one)
n_frames = min(len(files_a), len(files_b))
files_a = files_a[:n_frames]
files_b = files_b[:n_frames]

print(f"Rendering {n_frames} frames per sequence.")

center_a, extent_a = compute_global_bounds(files_a)
center_b, extent_b = compute_global_bounds(files_b)

renderer_a = pyrender.OffscreenRenderer(viewport_width=panel_w, viewport_height=panel_h)
renderer_b = pyrender.OffscreenRenderer(viewport_width=panel_w, viewport_height=panel_h)

raw_pairs = []
for i, (fa, fb) in enumerate(zip(files_a, files_b)):
    img_a = render_frame(renderer_a, fa, center_a, extent_a)
    img_b = render_frame(renderer_b, fb, center_b, extent_b)
    raw_pairs.append((img_a, img_b))
    if (i + 1) % 10 == 0:
        print(f"  Rendered {i + 1}/{n_frames} frames...")

renderer_a.delete()
renderer_b.delete()

print("Compositing frames and adding captions...")
composited = add_caption_bar(
    raw_pairs, caption_a, caption_b,
    panel_w, panel_h, caption_h, font_size
)

writer = imageio.get_writer(out_video, fps=fps)
for frame in composited:
    writer.append_data(frame)
writer.close()

# print(f"Saved video to: {out_video}")
