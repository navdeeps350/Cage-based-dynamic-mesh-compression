conda create -n myenv python=3.12
conda activate myenv
pip install -r requirements.txt

#####################################
       Compression Experiments
#####################################

Add the {action}Avg.obj (reference mesh) and {action}Avg_cage.obj (reference cage) files to the avg_meshes folder.

Add the {action}_mesh (folder contains mesh sequence in .obj format named mesh_0001.obj - mesh_000n.obj) 
and {action}_mesh_off (folder contains mesh sequence in .off format named mesh_0001.off - mesh_000n.off) 
folder to the original_meshes folder.

To run our pipeline, run pipeline_our_BLAS.py file by providing the following arguments:
action: name of the action (e.g., jumping, bouncing, etc.)
alpha (GLencoder parameter): a float value between starting from 0.25 to 6.0 with step size of 0.25
parameter_avg_mesh (average mesh encoding parameter): a float value like 0.001
Now you can run the pipeline_our_BLAS.py file.

After running the pipeline_our_BLAS.py file for all the parameters alpha, you need to remove the residual files.
Run the remove_residuals.py file.

To run the baseline pipeline, run pipeline_baseline.py file by providing the following arguments:
action: name of the action (e.g., jumping, bouncing, etc.)
alpha (GLencoder parameter): a float value between starting from 0.25 to 3.0 with step size of 0.25
Now you can run the pipeline_baseline.py file.

After running the pipeline_baseline.py file for all the parameters alpha, you need to remove the residual files.
Run the remove_residuals.py file.

Now you will have the results for both our pipeline and the baseline pipeline in the results folder.
To plot the results, run plot.py file by providing the following arguments:
action: name of the action (e.g., jumping, bouncing, etc.).

Finally you can visualize the results by running visualizer_render.py file by providing the following arguments:
obj_dir_a : directory of original mesh sequence 
obj_dir_b : directory of decompressed mesh sequence

#####################################
         Editing Experiments
#####################################

Add the {action}Avg.obj (reference mesh), {action}Avg_cage.obj (reference cage) and {action}Avg_modified.obj (reference modified mesh) files to the avg_meshes folder.
Run the mesh_editing.py file by providing the following arguments:
action: name of the action (e.g., jumping, bouncing, etc.)

Finally you can visualize the results by running visualizer_render.py file by providing the following arguments:
obj_dir_a : directory of original mesh sequence
obj_dir_b : directory of edited mesh sequence
