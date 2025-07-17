import os
import shutil
from PIL import Image
from tqdm import tqdm
import subprocess

SRC_DIR = "data/images"
DST_DIR = "data/upscaled_images"
os.makedirs(DST_DIR, exist_ok=True)

REALSERGAN_BIN = "/realesrgan-ncnn-vulkan-20220424-macos/realesrgan-ncnn-vulkan"
REALSERGAN_MODEL_DIR = "/realesrgan-ncnn-vulkan-20220424-macos/models"

def get_upscale_factor(width, height):
    min_dim = min(width, height)
    # 只允许2/3/4
    for factor in [2, 3, 4]:
        if min_dim * factor >= 768:
            return factor
    return 4  # 无法满足

def upscale_with_realesrgan(src_path, dst_path, scale):
    cmd = [
        REALSERGAN_BIN,
        "-i", src_path,
        "-o", dst_path,
        "-s", str(scale),
        "-f", "png",
        "-m", REALSERGAN_MODEL_DIR
    ]
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error upscaling {src_path}: {e}")
        return False

upscale_with_realesrgan('data/images/1001_0.png', 'data/upscaled_images/1001_0.png', 2)

# for fname in tqdm(os.listdir(SRC_DIR)):
#     if not fname.lower().endswith('.png'):
#         continue
#     src_path = os.path.join(SRC_DIR, fname)
#     dst_path = os.path.join(DST_DIR, fname)
#     im = Image.open(src_path)
#     w, h = im.size
#     if w < 512 or h < 512:
#         factor = get_upscale_factor(w, h)
#         print(f"Upscaling {fname} by {factor}x ...")
#         success = upscale_with_realesrgan(src_path, dst_path, factor)
#         if not success:
#             print(f"Failed to upscale {fname}, copying original.")
#             shutil.copy(src_path, dst_path)
#     else:
#         print(f"Image {fname} does not need upscaling, copying original.")
#         shutil.copy(src_path, dst_path)