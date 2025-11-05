import numpy as np
import os
import shutil

def ensure_dir(path: str):
    """Ensure the parent directory of the given path exists."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def safe_create_link_or_copy(src: str, dst: str):
    os.system("rm -r " + dst)
    os.system(f"ln -s {src} {dst}")

def convert_imu(input_path: str, output_path: str):
    """Convert IMU data from TUM-VI format to KITTI-360 style."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"IMU input file not found: {input_path}")

    with open(input_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    data = []
    for line in lines:
        parts = line.replace(',', ' ').split()
        if len(parts) == 7:
            try:
                row = [int(parts[0])] + [float(x) for x in parts[1:]]
                data.append(row)
            except ValueError:
                continue

    if not data:
        raise ValueError("No valid IMU data found.")

    arr = np.array(data)
    ts_s = arr[:, 0] / 1e9
    w_deg = arr[:, 1:4] * (180.0 / np.pi)
    a = arr[:, 4:7]
    result = np.column_stack([ts_s, w_deg, a])

    header = (
        "timestamp [s] w_RS_S_x [deg s^-1] w_RS_S_y [deg s^-1] w_RS_S_z [deg s^-1] "
        "a_RS_S_x [m s^-2] a_RS_S_y [m s^-2] a_RS_S_z [m s^-2]"
    )
    np.savetxt(output_path, result, fmt='%.9f', header=header, comments='#')
    print(f"IMU conversion complete. Saved to: {output_path}")

def convert_camera_timestamps(input_path: str, output_path: str):
    """Convert camera timestamp files from TUM-VI to KITTI-360 format."""
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Camera timestamp file not found: {input_path}")

    with open(input_path, 'r') as fin, open(output_path, 'w') as fout:
        fout.write("#timestamp [s] filename\n")
        for line in fin:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            if ',' in stripped:
                parts = stripped.split(',', 1)
            else:
                parts = stripped.split(None, 1)

            if len(parts) != 2:
                continue

            try:
                ts_ns = int(parts[0])
                filename = parts[1].strip()
                ts_s = ts_ns / 1e9
                fout.write(f"{ts_s:.9f} {filename}\n")
            except ValueError:
                continue

    print(f"Camera timestamp conversion complete. Saved to: {output_path}")

# ==================== Main Execution ====================
data_dir = "/home/gpcv/Data4/Datasets/tum/tum_vi/dataset-outdoors1_512_16/"
out_dir = "/home/gpcv/Data4/projects/SLAM/DSLAM/DROID/MASt3R-Fusion/datasets/tum_vi/dataset-outdoors1_512_16/"

# Input paths
imu_in = os.path.join(data_dir, "mav0/imu0/data.csv")
cam0_ts_in = os.path.join(data_dir, "mav0/cam0/data.csv")
cam1_ts_in = os.path.join(data_dir, "mav0/cam1/data.csv")

# Output paths
imu_out = os.path.join(out_dir, "kitti360/imu_data.txt")
cam0_ts_out = os.path.join(out_dir, "kitti360/cam0_timestamp.txt")
cam1_ts_out = os.path.join(out_dir, "kitti360/cam1_timestamp.txt")

# Symbolic link targets
cam0_data_src = os.path.join(data_dir, "mav0/cam0/data")
cam0_data_dst = os.path.join(out_dir, "kitti360/cam0_data")
cam1_data_src = os.path.join(data_dir, "mav0/cam1/data")
cam1_data_dst = os.path.join(out_dir, "kitti360/cam1_data")

# Ensure output directories exist
ensure_dir(imu_out)
ensure_dir(cam0_ts_out)
ensure_dir(cam1_ts_out)

# Perform conversions
convert_imu(imu_in, imu_out)
convert_camera_timestamps(cam0_ts_in, cam0_ts_out)
convert_camera_timestamps(cam1_ts_in, cam1_ts_out)

# Create symbolic links
safe_create_link_or_copy(cam0_data_src, cam0_data_dst)
safe_create_link_or_copy(cam1_data_src, cam1_data_dst)

run_txt = os.path.join(out_dir, "run_tumvi.sh")
with open(run_txt, 'w') as f:
    run_str = f"python main.py --dataset {cam0_data_dst} --config config/base_tumvi.yaml --calib config/intrinsics_tumvi.yaml --imu_path {imu_out} --imu_dt 0 --stamp_path {cam0_ts_out} --result_path result_tumvi.txt --save_h5\n"
    f.write(run_str)
print("Run command:")
print(run_str)