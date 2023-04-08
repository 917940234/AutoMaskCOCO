import os, copy
import numpy as np

from salt.onnx_model import OnnxModel
from salt.dataset_explorer import DatasetExplorer
from salt.display_utils import DisplayUtils

class CurrentCapturedInputs:
    def __init__(self):
        self.input_point = np.array([])
        self.input_label = np.array([])
        self.low_res_logits = None
        self.curr_mask = None

    def reset_inputs(self):
        self.input_point = np.array([])
        self.input_label = np.array([])
        self.low_res_logits = None
        self.curr_mask = None

    def set_mask(self, mask):
        self.curr_mask = mask

    def add_input_click(self, input_point, input_label):
        if len(self.input_point) == 0:
            self.input_point = np.array([input_point])
        else:
            self.input_point = np.vstack([self.input_point, np.array([input_point])])
        self.input_label = np.append(self.input_label, input_label)

    def set_low_res_logits(self, low_res_logits):
        self.low_res_logits = low_res_logits


class Editor:
    def __init__(self, onnx_model_path, dataset_path, categories=None, coco_json_path=None):
        self.dataset_path = dataset_path
        self.coco_json_path = coco_json_path
        self.onnx_model_path = onnx_model_path
        self.onnx_helper = OnnxModel(self.onnx_model_path)
        if categories is None and not os.path.exists(coco_json_path):
            raise ValueError("categories must be provided if coco_json_path is None")
        if self.coco_json_path is None:
            self.coco_json_path = os.path.join(self.dataset_folder, "annotations.json")
        self.dataset_explorer = DatasetExplorer(
            "dataset", categories=categories, coco_json_path=self.coco_json_path
        )
        self.curr_inputs = CurrentCapturedInputs()
        self.categories = self.dataset_explorer.get_categories()
        self.image_id = 0
        self.category_id = 0
        self.show_other_anns = True
        (
            self.image,
            self.image_bgr,
            self.image_embedding,
        ) = self.dataset_explorer.get_image_data(self.image_id)
        self.display = self.image_bgr.copy()
        self.du = DisplayUtils()
        self.reset()

    def add_click(self, new_pt, new_label):
        self.curr_inputs.add_input_click(new_pt, new_label)
        masks, low_res_logits = self.onnx_helper.call(
            self.image,
            self.image_embedding,
            self.curr_inputs.input_point,
            self.curr_inputs.input_label,
            low_res_logits=self.curr_inputs.low_res_logits,
        )
        self.display = self.du.draw_points(
            self.display, self.curr_inputs.input_point, self.curr_inputs.input_label
        )
        self.display = self.du.overlay_mask_on_image(self.display, masks[0, 0, :, :])
        self.curr_inputs.set_mask(masks[0, 0, :, :])
        self.curr_inputs.set_low_res_logits(low_res_logits)

    def draw_known_annotations(self):
        anns, colors = self.dataset_explorer.get_annotations(
            self.image_id, return_colors=True
        )
        self.display = self.du.draw_annotations(self.display, anns, colors)

    def reset(self, hard=True):
        self.curr_inputs.reset_inputs()
        self.display = self.image_bgr.copy()
        if self.show_other_anns:
            self.draw_known_annotations()

    def toggle_anns(self):
        self.show_other_anns = not self.show_other_anns
        self.reset()
    
    def step_up_transparency(self):
        self.du.increase_transparency()
        self.reset()

    def step_down_transparency(self):
        self.du.increase_transparency()
        self.reset()

    def save_ann(self):
        self.dataset_explorer.add_annotation(
            self.image_id, self.category_id, self.curr_inputs.curr_mask
        )

    def save(self):
        self.dataset_explorer.save_annotation()

    def next_image(self):
        if self.image_id == self.dataset_explorer.get_num_images() - 1:
            return
        self.image_id += 1
        (
            self.image,
            self.image_bgr,
            self.image_embedding,
        ) = self.dataset_explorer.get_image_data(self.image_id)
        self.display = self.image_bgr.copy()
        self.reset()

    def prev_image(self):
        if self.image_id == 0:
            return
        self.image_id -= 1
        (
            self.image,
            self.image_bgr,
            self.image_embedding,
        ) = self.dataset_explorer.get_image_data(self.image_id)
        self.display = self.image_bgr.copy()
        self.reset()

    def next_category(self):
        if self.category_id == len(self.categories) - 1:
            return
        self.category_id += 1

    def prev_category(self):
        if self.category_id == 0:
            return
        self.category_id -= 1
    
    def select_category(self, category_id):
        self.category_id = category_id
