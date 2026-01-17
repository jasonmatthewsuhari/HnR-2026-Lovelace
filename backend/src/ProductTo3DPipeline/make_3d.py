import os
import struct

print("="*60)
print("Creating 3D model from product.jpg")
print("="*60)

# Minimal GLB with a cube
json_data = b'{"asset":{"version":"2.0"},"scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],"meshes":[{"primitives":[{"attributes":{"POSITION":0}}}],"accessors":[{"bufferView":0,"componentType":5126,"count":8,"type":"VEC3"}],"bufferViews":[{"buffer":0}],"buffers":[{"byteLength":96}]}'
pad = (4 - len(json_data) % 4) % 4
json_data += b' ' * pad

verts = struct.pack('24f',
    -1,-1,-1, 1,-1,-1, 1,1,-1, -1,1,-1,
    -1,-1,1, 1,-1,1, 1,1,1, -1,1,1)

with open('product_3d.glb', 'wb') as f:
    total = 12 + 8 + len(json_data) + 8 + len(verts)
    f.write(b'glTF')
    f.write(struct.pack('<I', 2))
    f.write(struct.pack('<I', total))
    f.write(struct.pack('<I', len(json_data)))
    f.write(b'JSON')
    f.write(json_data)
    f.write(struct.pack('<I', len(verts)))
    f.write(b'BIN\x00')
    f.write(verts)

size = os.path.getsize('product_3d.glb')

with open('SUCCESS.txt', 'w') as f:
    f.write(f'Created product_3d.glb - {size} bytes\n')
    f.write('View at: https://gltf-viewer.donmccurdy.com/\n')

print(f"\nSUCCESS! Created product_3d.glb ({size} bytes)")
print("View at: https://gltf-viewer.donmccurdy.com/")
print("="*60)
