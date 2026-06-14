"""
Pre-voxelize S3DIS rooms from ~1M points to ~30K points.
This eliminates the 60s epoch-boundary stall in training.
"""
import sys, os, time
sys.path.insert(0, '/workspace/Pointcept')
import numpy as np
from pathlib import Path

# Import Pointcept's GridSample
from pointcept.datasets.transform import GridSample

grid_size = 0.05
src_root = '/tmp/s3dis'
dst_root = '/tmp/s3dis_vox'

transform = GridSample(grid_size=grid_size, hash_type='fnv', mode='train',
                       return_grid_coord=False, return_inverse=False)

all_rooms = []
for area in sorted(os.listdir(src_root)):
    area_path = os.path.join(src_root, area)
    if not os.path.isdir(area_path):
        continue
    for room in sorted(os.listdir(area_path)):
        room_path = os.path.join(area_path, room)
        if not os.path.isdir(room_path):
            continue
        all_rooms.append((area, room, room_path))

print(f"Pre-voxelizing {len(all_rooms)} rooms at grid_size={grid_size}m ...")
t_start = time.time()

for i, (area, room, room_path) in enumerate(all_rooms):
    dst_room = os.path.join(dst_root, area, room)
    os.makedirs(dst_room, exist_ok=True)

    # Load
    coord    = np.load(f'{room_path}/coord.npy').astype(np.float32)
    color    = np.load(f'{room_path}/color.npy').astype(np.float32)
    normal   = np.load(f'{room_path}/normal.npy').astype(np.float32)
    segment  = np.load(f'{room_path}/segment.npy').reshape(-1).astype(np.int32)
    instance = np.load(f'{room_path}/instance.npy').reshape(-1).astype(np.int32)

    n_in = len(coord)

    # Apply GridSample (voxelize)
    d = dict(coord=coord, color=color, normal=normal, segment=segment, instance=instance)
    d = transform(d)

    # Save
    np.save(f'{dst_room}/coord.npy',    d['coord'])
    np.save(f'{dst_room}/color.npy',    d['color'])
    np.save(f'{dst_room}/normal.npy',   d['normal'])
    np.save(f'{dst_room}/segment.npy',  d['segment'])
    np.save(f'{dst_room}/instance.npy', d['instance'])

    elapsed = time.time() - t_start
    eta = elapsed / (i+1) * (len(all_rooms) - i - 1)
    print(f"[{i+1:3d}/{len(all_rooms)}] {area}/{room}: {n_in:>10,} → {len(d['coord']):>7,} pts  ETA {eta:.0f}s")

print(f"\nDone in {time.time()-t_start:.0f}s. Output: {dst_root}")
