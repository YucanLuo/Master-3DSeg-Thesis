import math, os, random
import numpy as np
import torch
from torch.utils.data import Dataset
import open3d as o3d
from ..ops import voxelization_idx
from pye57 import E57


class HouseDataset(Dataset):
    CLASSES = None

    def __init__(self,
                 data_root,
                 prefix,
                 suffix,
                 voxel_cfg=None,
                 training=True,
                 repeat=1,
                 compute_offset=False,
                 tta=False,
                 logger=None):
        self.data_root = data_root
        self.prefix = prefix  # 前缀
        self.suffix = suffix  # 尾缀
        self.voxel_cfg = voxel_cfg
        self.training = training
        self.repeat = repeat
        self.tta = tta
        self.logger = logger
        self.compute_offset = compute_offset
        self.mode = 'train' if training else 'test'
        self.ota = False if training else True
        self.filenames = self.get_filenames()
        self.logger.info(f'Load {self.mode} dataset: {len(self.filenames)} scans')

    def get_filenames(self):
        filenames = os.listdir(self.data_root)
        assert len(filenames) > 0, 'Empty dataset.'
        filenames = sorted(filenames * self.repeat)
        return filenames

    def load(self, filename):
        return np.load(f'{self.data_root}/{filename}')

    def __len__(self):
        return len(self.filenames)

    def getInstanceInfo(self, xyz, instance_label, semantic_label):
        pt_mean = np.ones((xyz.shape[0], 3), dtype=np.float32) * -100.0
        instance_pointnum = []
        instance_cls = []
        instance_num = int(instance_label.max()) + 1
        for i_ in range(instance_num):
            inst_idx_i = np.where(instance_label == i_)  # 该对象的所在点
            xyz_i = xyz[inst_idx_i]
            pt_mean[inst_idx_i] = xyz_i.mean(0)  # 中心点
            instance_pointnum.append(inst_idx_i[0].size)  # 该对象点数量
            cls_idx = inst_idx_i[0][0]  # 这个对象的其中一个点
            instance_cls.append(semantic_label[cls_idx])  # 这个对象的类别
        pt_offset_label = pt_mean - xyz  # 相对于各个对象的偏移
        return instance_num, instance_pointnum, instance_cls, pt_offset_label

    def dataAugment(self, xyz, jitter=False, flip=False, rot=False, scale=False, prob=1.0):
        m = np.eye(3)
        if jitter and np.random.rand() < prob:  # 平移抖动
            xyz += np.array([random.uniform(-2, 2), random.uniform(-2, 2), 0])
        if flip and np.random.rand() < prob:
            m[0][0] *= np.random.randint(0, 2) * 2 - 1  # +-1
        if scale and np.random.rand() < prob:  # 随机缩放
            xyz[:, 0:1] *= random.uniform(0.7, 1.3)
            xyz[:, 1:2] *= random.uniform(0.7, 1.3)
        if rot and np.random.rand() < prob:
            theta = np.random.rand() * 2 * math.pi  # 360度旋转
            m = np.matmul(m, [[math.cos(theta), math.sin(theta), 0],
                              [-math.sin(theta), math.cos(theta), 0],
                              [0, 0, 1]])
        # else:
        #     # 根据经验，稍微旋转场景可以匹配检查点的结果  0, 0.5, 1, 1.5
        #     theta = 0.5 * math.pi
        #     m = np.matmul(m, [[math.cos(theta), math.sin(theta), 0],
        #                       [-math.sin(theta), math.cos(theta), 0], [0, 0, 1]])

        return np.matmul(xyz, m)

    def crop(self, xyz, step=32):  # 裁剪
        xyz_offset = xyz.copy()
        valid_idxs = xyz_offset.min(1) >= 0
        assert valid_idxs.sum() == xyz.shape[0]
        spatial_shape = np.array([self.voxel_cfg.spatial_shape[1]] * 3)  # array([512, 512, 512])
        room_range = xyz.max(0) - xyz.min(0)
        while valid_idxs.sum() > int(len(valid_idxs) * 0.8) or valid_idxs.sum() > self.voxel_cfg.max_npoint:
            step_temp = step
            if valid_idxs.sum() > 1e6:
                step_temp = step * 2
            offset = np.clip(spatial_shape - room_range + 0.001, None, 0) * np.random.rand(3)  # 裁剪过大的房间
            xyz_offset = xyz + offset
            valid_idxs = (xyz_offset.min(1) >= 0) * ((xyz_offset < spatial_shape).sum(1) == 3)
            spatial_shape[:2] -= step_temp
        return xyz_offset, valid_idxs

    def crop2(self, xyz):  # 裁剪
        room_range = xyz.max(0) - xyz.min(0)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(xyz)
        for i in range(5):
            box = o3d.geometry.AxisAlignedBoundingBox()
            min_size = np.random.rand(3) * room_range
            box.min_bound = min_size
            box.max_bound = min_size + np.array(
                [np.random.uniform(0.2, 0.5),
                 np.random.uniform(0.2, 0.5),
                 np.random.uniform(0.2, 0.5)]) * room_range

            plane_inds = box.get_point_indices_within_bounding_box(pcd.points)
            pcd = pcd.select_by_index(plane_inds, invert=True)
        return np.array(pcd.points)


    def getCroppedInstLabel(self, instance_label, valid_idxs):  # oj=0,1,2,5时，5--》3
        instance_label = instance_label[valid_idxs]
        j = 0
        while j < instance_label.max():
            if len(np.where(instance_label == j)[0]) == 0:
                instance_label[instance_label == instance_label.max()] = j
            j += 1
        return instance_label

    def down_sample_drop(self, xyz, rgb, semantic_label, instance_label, drop_prob=0.1, min_voxel=0.01, max_voxel=0.03):
        xyz_ls, rgb_ls, selabel_ls = [], [], []
        for i in range(np.max(instance_label)+1):
            if np.random.random() > drop_prob:
                ind = instance_label == i
                pcd = o3d.geometry.PointCloud()
                pcd.points = o3d.utility.Vector3dVector(xyz[ind])
                pcd.colors = o3d.utility.Vector3dVector(rgb[ind])
                ratio = np.round(np.random.uniform(min_voxel, max_voxel), 3)
                pcd = pcd.voxel_down_sample(ratio)
                xyz_ls.append(np.array(pcd.points))
                rgb_ls.append(np.array(pcd.colors))
                cate = np.unique(semantic_label[ind])
                selabel_ls.append(np.ones(len(pcd.colors))*cate)
        return np.concatenate(xyz_ls), np.concatenate(rgb_ls), np.concatenate(selabel_ls)




    def transform_train(self, xyz, rgb, semantic_label, instance_label, aug_prob=1.0):
        # xyz 单位：米
        # semantic_label 0~19 -100;  instance_label 0~instance_num-1 -100
        xyz_middle = self.dataAugment(xyz, True, True, True, True, aug_prob)
        xyz = xyz_middle * self.voxel_cfg.scale  # 50
        xyz = xyz - xyz.min(0)

        # max_tries = 5  # crop
        # while max_tries > 0:
        #     xyz_offset, valid_idxs = self.crop(xyz)
        #     if valid_idxs.sum() >= self.voxel_cfg.min_npoint:  # 20000
        #         xyz = xyz_offset
        #         break
        #     max_tries -= 1
        # if valid_idxs.sum() < self.voxel_cfg.min_npoint:
        #     return None
        # xyz = xyz[valid_idxs]
        # xyz_middle = xyz_middle[valid_idxs]  # 得到没有移动过的点
        # rgb = rgb[valid_idxs]
        # semantic_label = semantic_label[valid_idxs]

        xyz, rgb, semantic_label = self.down_sample_drop(xyz, rgb, semantic_label, instance_label, drop_prob=0.1, min_voxel=0.01, max_voxel=0.03)
        xyz_middle = xyz / self.voxel_cfg.scale
        # print('????', xyz.shape, xyz_middle.shape, rgb.shape, semantic_label.shape)
        if self.compute_offset:
            # instance_label = self.getCroppedInstLabel(instance_label, valid_idxs) # crop
            return xyz, xyz_middle, rgb, semantic_label, instance_label
        else:
            return xyz, xyz_middle, rgb, semantic_label, None

    def transform_test(self, xyz, rgb, semantic_label, instance_label):
        xyz_middle = self.dataAugment(xyz, False, False, False, False)
        xyz = xyz_middle * self.voxel_cfg.scale  # 50
        xyz -= xyz.min(0)
        valid_idxs = np.ones(xyz.shape[0], dtype=bool)
        if self.compute_offset:
            instance_label = self.getCroppedInstLabel(instance_label, valid_idxs)
            return xyz, xyz_middle, rgb, semantic_label, instance_label
        else:
            return xyz, xyz_middle, rgb, semantic_label, None

    def __getitem__(self, index):
        filename = self.filenames[index]
        data = self.load(filename)
        xyz = np.stack([data['x'], data['y'], data['z']], axis=1)
        xyz -= np.mean(xyz, axis=0)
        xyz[:, -1] -= np.min(xyz[:, -1])
        # color_normals = np.stack([data['g'], data['n1'], data['n2'], data['n3']], axis=1)
        color_normals = np.expand_dims(data['g'], axis=-1).repeat(3, axis=-1)
        semantic_label = data['cate']
        instance_label = data['oj']# if self.compute_offset else None
        if self.training:
            data = self.transform_train(xyz, color_normals, semantic_label, instance_label)
        else:
            data = self.transform_test(xyz, color_normals, semantic_label, instance_label)
        if data is None:
            return None
        xyz, xyz_middle, rgb, semantic_label, instance_label = data  # 放大的点，原始增强点，颜色，分类，oj_id
        feat = torch.from_numpy(rgb).float()
        semantic_label = torch.from_numpy(semantic_label)
        if not self.training and self.tta:  # for test
            theta_ls = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75] if self.tta else [0]
            xyz_middle_ls = [self.rot_xyz(xyz_middle, theta) for theta in theta_ls]
            xyz_ls = [xyz_middle * self.voxel_cfg.scale for xyz_middle in xyz_middle_ls]
            xyz_ls = [xyz - xyz.min(0) for xyz in xyz_ls]
            return filename, xyz_ls, xyz_middle_ls, feat, semantic_label

        coord = torch.from_numpy(xyz).long()
        coord_float = torch.from_numpy(xyz_middle)
        if self.training:
            # feat[:, 0] += torch.randn(1) * 0.1  # g+normal
            feat += torch.randn(3) * 0.1  # rgb
        if self.compute_offset:
            info = self.getInstanceInfo(xyz_middle, instance_label.astype(np.int8), semantic_label)
            inst_num, inst_pointnum, inst_cls, pt_offset_label = info
            # oj_num, 每个对象的点数, 对应的分类，相对于对象中心点的偏移
            instance_label = torch.from_numpy(instance_label)
            pt_offset_label = torch.from_numpy(pt_offset_label)
            return (1, coord, coord_float, feat, semantic_label, instance_label, inst_num,
                    inst_pointnum, inst_cls, pt_offset_label)
        else:
            return filename, None, coord, coord_float, feat, semantic_label, None, None, None, None, None

    def collate_fn(self, batch):
        scan_ids, coords, coords_float, feats = [], [], [], []
        semantic_labels, instance_labels, instance_pointnum = [], [], []
        instance_cls, pt_offset_labels, filename_ls = [], [], []
        total_inst_num, batch_id = 0, 0
        for data in batch:
            if data is None:
                continue
            (filename, scan_id, coord, coord_float, feat, semantic_label, instance_label, inst_num,
             inst_pointnum, inst_cls, pt_offset_label) = data
            # id, xyz int, xyz float, rgb, 分类, oj_id, 当前oj总数, 每个对象的点数, 对应的分类，相对于对象中心点的偏移
            coords.append(torch.cat([coord.new_full((coord.size(0), 1), batch_id), coord], 1))  # xyzb
            coords_float.append(coord_float)
            feats.append(feat)
            semantic_labels.append(semantic_label)
            filename_ls.append(filename)
            if self.compute_offset:
                instance_label[np.where(instance_label != -100)] += total_inst_num  # 转换为batch下的计数
                total_inst_num += inst_num
                scan_ids.append(scan_id)
                instance_labels.append(instance_label)
                instance_pointnum.extend(inst_pointnum)
                instance_cls.extend(inst_cls)
                pt_offset_labels.append(pt_offset_label)
            batch_id += 1
        assert batch_id > 0, 'empty batch'
        if batch_id < len(batch):
            self.logger.info(f'batch is truncated from size {len(batch)} to {batch_id}')

        # merge all the scenes in the batch
        coords = torch.cat(coords, 0)  # long (N, 1 + 3), the batch item idx is put in coords[:, 0]
        batch_idxs = coords[:, 0].int()
        coords_float = torch.cat(coords_float, 0).to(torch.float32)  # float (N, 3)
        feats = torch.cat(feats, 0)  # float (N, C)
        semantic_labels = torch.cat(semantic_labels, 0).long()  # long (N)
        if self.compute_offset:
            instance_labels = torch.cat(instance_labels, 0).long()  # long (N)
            instance_pointnum = torch.tensor(instance_pointnum, dtype=torch.int)  # int (total_nInst)
            instance_cls = torch.tensor(instance_cls, dtype=torch.long)  # long (total_nInst)
            pt_offset_labels = torch.cat(pt_offset_labels).float()

        spatial_shape = np.clip(
            coords.max(0)[0][1:].numpy() + 1, self.voxel_cfg.spatial_shape[0], None)  # 20
        voxel_coords, v2p_map, p2v_map = voxelization_idx(coords, batch_id)
        res = {
            'filenames': filename_ls,
            'scan_ids': scan_ids,  # 0
            'coords': coords,  # xyz*scale
            'batch_idxs': batch_idxs,  # 批次id
            'voxel_coords': voxel_coords,  # 下采样后的点
            'p2v_map': p2v_map,  # 映射
            'v2p_map': v2p_map,  # 映射
            'coords_float': coords_float,  # xyz
            'feats': feats,  # rgb
            'semantic_labels': semantic_labels,  # cls
            'instance_labels': instance_labels,  # oj_id
            'instance_pointnum': instance_pointnum,  # 每个oj有多少个点
            'instance_cls': instance_cls,  # oj 对应的分类
            'pt_offset_labels': pt_offset_labels,  # oj相对于oj中心点的偏移
            'spatial_shape': spatial_shape,  # 限定最小尺寸
            'batch_size': batch_id,
        }
        return res

    def collate_fn_test(self, batch):
        assert len(batch) == 1, 'batch must be 1'
        batch_id = 0
        filename, coord_ls, coord_float_ls, feats, semantic_labels = batch[0]
        res = {
            'filename': filename,
            'feats': feats,
            'batch_size': 1,
            'semantic_labels': semantic_labels
        }
        for k, (coord, coord_float) in enumerate(zip(coord_ls, coord_float_ls)):
            coord = torch.from_numpy(coord).long()
            coord_float = torch.from_numpy(coord_float).to(torch.float32)
            coord = torch.cat([coord.new_full((coord.size(0), 1), batch_id), coord], 1)
            spatial_shape = np.clip(coord.max(0)[0][1:].numpy() + 1, self.voxel_cfg.spatial_shape[0], None)  # 20
            voxel_coords, v2p_map, p2v_map = voxelization_idx(coord, 1)
            if k == 0:
                res.update(dict(voxel_coords=voxel_coords, p2v_map=p2v_map, v2p_map=v2p_map,
                                coords_float=coord_float, spatial_shape=spatial_shape))
            else:
                res[f'voxel_coords_{k}'] = voxel_coords
                res[f'p2v_map_{k}'] = p2v_map
                res[f'v2p_map_{k}'] = v2p_map
                res[f'coords_float_{k}'] = coord_float
                res[f'spatial_shape_{k}'] = spatial_shape
        return res


    def rot_xyz(self, xyz, theta):
        m = np.eye(3)
        theta *= math.pi
        m = np.matmul(m, [[math.cos(theta), math.sin(theta), 0],
                          [-math.sin(theta), math.cos(theta), 0], [0, 0, 1]])
        xyz = np.matmul(xyz, m)
        xyz -= np.mean(xyz, axis=0)
        xyz[:, -1] -= np.min(xyz[:, -1])
        return xyz


class DemoDataset:
    def __init__(self, path, o3d_voxel_size=0.01, voxel_cfg=None):
        self.path = path
        self.filenames = os.listdir(path)
        self.o3d_voxel_size = o3d_voxel_size
        self.voxel_cfg = voxel_cfg
        self.tta = True

    def __len__(self):
        return len(self.filenames)


    def collate_fn(self, batch):
        assert len(batch) == 1, 'batch must be 1'
        batch_id = 0
        filename, coord_ls, coord_float_ls, feats = batch[0]
        res = {
            'filename': filename,
            'feats': feats,
            'batch_size': 1,
        }
        for k, (coord, coord_float) in enumerate(zip(coord_ls, coord_float_ls)):
            coord = torch.from_numpy(coord).long()
            coord_float = torch.from_numpy(coord_float).to(torch.float32)
            coord = torch.cat([coord.new_full((coord.size(0), 1), batch_id), coord], 1)
            spatial_shape = np.clip(coord.max(0)[0][1:].numpy() + 1, self.voxel_cfg.spatial_shape[0], None)  # 20
            voxel_coords, v2p_map, p2v_map = voxelization_idx(coord, 1)
            if k == 0:
                res.update(dict(voxel_coords=voxel_coords, p2v_map=p2v_map, v2p_map=v2p_map,
                                coords_float=coord_float, spatial_shape=spatial_shape))
            else:
                res[f'voxel_coords_{k}'] = voxel_coords
                res[f'p2v_map_{k}'] = p2v_map
                res[f'v2p_map_{k}'] = v2p_map
                res[f'coords_float_{k}'] = coord_float
                res[f'spatial_shape_{k}'] = spatial_shape
        return res

    def __getitem__(self, index):
        filename = self.filenames[index]

        if filename.endswith('e57'):
            with E57(f'{self.path}/{filename}') as e57:
                data = e57.read_scan(index=0, intensity=True, colors=False,
                                     ignore_missing_fields=True)
            xyz = np.stack([data[k] for k in ['cartesianX', 'cartesianY', 'cartesianZ']], axis=-1)
            colors = np.expand_dims(data['intensity'], axis=-1).repeat(3, axis=-1)
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(xyz)
            pcd.colors = o3d.utility.Vector3dVector(colors)
        else:
            pcd = o3d.io.read_point_cloud(f'{self.path}/{filename}')
        pcd = pcd.voxel_down_sample(self.o3d_voxel_size)
        # pcd.estimate_normals()
        # normals = np.array(pcd.normals)
        xyz_middle, feats = np.array(pcd.points), np.array(pcd.colors)
        # feats = np.concatenate([colors, normals], axis=1) # np.expand_dims(np.array(pcd.colors)[:, 0], axis=-1)

        theta_ls = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75] if self.tta else [0]
        xyz_middle_ls = [self.rot_xyz(xyz_middle, theta) for theta in theta_ls]
        xyz_ls = [xyz_middle * self.voxel_cfg.scale for xyz_middle in xyz_middle_ls]
        xyz_ls = [xyz-xyz.min(0) for xyz in xyz_ls]
        feats = torch.from_numpy(feats).float()
        return filename, xyz_ls, xyz_middle_ls, feats

    def rot_xyz(self, xyz, theta):
        m = np.eye(3)
        theta *= math.pi
        m = np.matmul(m, [[math.cos(theta), math.sin(theta), 0],
                          [-math.sin(theta), math.cos(theta), 0], [0, 0, 1]])
        xyz = np.matmul(xyz, m)
        xyz -= np.mean(xyz, axis=0)
        xyz[:, -1] -= np.min(xyz[:, -1])
        return xyz

