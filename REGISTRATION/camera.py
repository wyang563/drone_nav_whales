from Localization.hloc import extract_features, match_features, reconstruction, visualization, pairs_from_exhaustive
from Localization.hloc.visualization import plot_images, read_image
from Localization.hloc.utils import viz_3d
from pathlib import Path
from tqdm import tqdm
import pycolmap
from Localization.hloc.localize_sfm import QueryLocalizer, pose_from_cluster

outputs = Path('Localization/outputs/')
sfm_pairs = outputs / 'pairs-sfm.txt'
loc_pairs = outputs / 'pairs-loc.txt'
sfm_dir = outputs / 'sfm'
features = outputs / 'features.h5'
matches = outputs / 'matches.h5'
feature_conf = extract_features.confs['disk']
matcher_conf = match_features.confs['disk+lightglue']

# images processed by drone
def plot_drone_images(images, references):
    print("Plotting drone images")
    plot_images([read_image(images / r) for r in references], dpi=25)

def plot_3d_reconstruction(model):
    fig = viz_3d.init_figure()
    viz_3d.plot_reconstruction(fig, model, color='rgba(255,0,0,0.5)', name="mapping", points_rgb=True)
    fig.show()

# Extract features
def get_extraction_model(images_file_path):
    images = Path(images_file_path) # TODO replace with drone path to images
    references = [str(p.relative_to(images)) for p in (images / 'mapping/').iterdir()]
    print("Extracting features from images")
    extract_features.main(feature_conf, images, image_list=references, feature_path=features)
    pairs_from_exhaustive.main(sfm_pairs, image_list=references)
    match_features.main(matcher_conf, sfm_pairs, features=features, matches=matches)
    return reconstruction.main(sfm_dir, images, sfm_pairs, features, matches, image_list=references)

def localization(model, images, query):
    references_registered = [model.images[i].name for i in model.reg_image_ids()]
    extract_features.main(feature_conf, images, image_list=[query], feature_path=features, overwrite=True)
    pairs_from_exhaustive.main(loc_pairs, image_list=[query], ref_list=references_registered)
    match_features.main(matcher_conf, loc_pairs, features=features, matches=matches, overwrite=True);


