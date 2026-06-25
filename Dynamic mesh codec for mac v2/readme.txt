This is a dynamic mesh codec. The basic usage can be seen in the encode.sh and decode.sh scripts. The encoding script is as follows:

./LaplaceMeshCodec -ed samba "mesh_[0-9]+\.obj" out.bin 0.9 4 avgSamba.obj

here is the meaning of the parameters:
-ed 
encode dynamic, i.e. tells the codec that the task is to encode.

samba 
folder with input files.

"mesh_[0-9]+\.obj" 
regular expression for input files.

out.bin
output file name

0.9
target data rate in bpfv, i.e. bits per frame per vertex.

4
selects a particular flavor of laplacian used for encoding. 4 means cotan laplacian with error propagation control. Keep set to 4 in all experiments.

avgSamba.obj
name of file with average mesh. Use the avgmesh tool to generate one. Will be used to construct the geometric laplacian used for encoding the sequence.


The decoding script is as follows:

./LaplaceMeshCodec -dd out.bin decoded//recon 4

here is the meaning of the parameters:
-dd
decode dynamic, i.e. tells the coded that the task is to decode.

out.bin
name of the file to be decoded. The file must be previously created by the same coded by a -ed call.

decoded//recon
folder and file name prefix for the output. The output folder must exist (decoded), output files will be created in numbered sequence with .obj extension.

4
selects a particular flavor of laplacian used for encoding. 4 means cotan laplacian with error propagation control. Must be the same as the one used for encoding. Keep set to 4 in all experiments.