Usage:
Encoding:
EPC_Codec.exe -e <filename.obj> <targetfile.bin> 0.01 2
- change the 0.01 constant to something else in order to get higher/lower data rate
- keep the constant 2 unchanged

Decoding
EPC_Codec.exe -d decode <targetfile.bin> 2
- don't forget the constant 2
- the vertex order and triangle order will be different!

Reindexing
EPC_Codec.exe -r <filenam.obj> <reindexed.obj>
- does not change vertex coordinates
- only changes vertex order and triangle order
- result should match decoded meshes => can be used for eavluation
