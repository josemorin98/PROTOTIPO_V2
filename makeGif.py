import glob
from PIL import Image

# filepaths
# fp_in = "/path/to/image_*.png"
fp_in = "tests_gamma/Correlations/w5/correlation_3/temp_*"
fp_out = "./prueba.gif"

# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
imgs = (Image.open(f) for f in sorted(glob.glob(fp_in)))
img = next(imgs)  # extract first image from iterator
durationInMS = 2000
img.save(fp=fp_out, format='GIF', append_images=imgs,
         save_all=True, duration=durationInMS, loop=0)