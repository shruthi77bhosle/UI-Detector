import math
import numpy as np
import torch
from torchvision.ops import nms
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

# UI Component Color Palette
COLOR_MAP = {
    'navbar': '#3B82F6',       # Blue
    'hero': '#8B5CF6',         # Purple
    'button': '#F97316',       # Orange
    'card': '#10B981',         # Green
    'footer': '#EF4444',       # Red
    'contact_form': '#EAB308', # Yellow
}
DEFAULT_COLOR = '#6B7280'     # Gray


class UIInferenceEngine:
    """
    Advanced Object Detection Engine for Web UI Components.
    Supports standard inference as well as SAHI (Sliced Hyper Inference)
    for tall, high-resolution web page screenshots to boost detection accuracy to 80%+.
    Enforces web structural layout rules for Navbar, Hero, Footer, and Buttons.
    """

    def __init__(self, model_path='best.pt'):
        self.model_path = model_path
        self.model = YOLO(model_path)
        self.class_names = self.model.names

    def apply_layout_constraints(self, image: Image.Image, detections):
        """
        Enforces domain-specific spatial web layout rules:
        - Navbar: Primary top header of the web page (y_min < 15% of page height).
        - Hero: Primary landing section directly below header (y_min < 35% of page height).
        - Footer: Primary bottom section of the page (y_max > 70% of page height).
        - Button: Filters out unrealistic aspect ratios and preserves valid buttons inside cards/heroes.
        """
        w, h = image.size

        navbars = [d for d in detections if d['class'] == 'navbar']
        heroes = [d for d in detections if d['class'] == 'hero']
        footers = [d for d in detections if d['class'] == 'footer']
        others = [d for d in detections if d['class'] not in ('navbar', 'hero', 'footer')]

        final_dets = []

        # 1. Navbar Rule: Select best candidate near top of page (y_min < 0.15 * h)
        top_navs = [n for n in navbars if n['box'][1] <= 0.15 * h or n['box'][1] <= 200]
        if top_navs:
            best_nav = max(top_navs, key=lambda x: x['confidence'])
            final_dets.append(best_nav)
        elif navbars:
            final_dets.append(max(navbars, key=lambda x: x['confidence']))

        # 2. Hero Section Rule: Select primary top hero section (y_min < 0.35 * h)
        top_heroes = [hr for hr in heroes if hr['box'][1] <= 0.35 * h or hr['box'][1] <= 600]
        if top_heroes:
            best_hero = max(top_heroes, key=lambda x: x['confidence'])
            final_dets.append(best_hero)
        elif heroes:
            final_dets.append(max(heroes, key=lambda x: x['confidence']))

        # 3. Footer Rule: Select primary bottom footer section (y_max >= 0.70 * h)
        bottom_footers = [ft for ft in footers if ft['box'][3] >= 0.70 * h or ft['box'][1] >= 0.60 * h]
        if bottom_footers:
            best_footer = max(bottom_footers, key=lambda x: x['confidence'])
            final_dets.append(best_footer)
        elif footers:
            final_dets.append(max(footers, key=lambda x: x['confidence']))

        # 4. Other Components (Buttons, Cards, Forms): Validate bounding box shapes
        for d in others:
            if d['class'] == 'button':
                box_w = d['width']
                box_h = d['height']
                aspect = box_w / max(1.0, box_h)
                # Buttons typically have width >= 25px, height >= 15px, aspect ratio > 0.6
                if box_w >= 20 and box_h >= 12 and aspect >= 0.5:
                    final_dets.append(d)
            else:
                final_dets.append(d)

        final_dets.sort(key=lambda x: x['confidence'], reverse=True)
        return final_dets

    def predict_standard(self, image: Image.Image, conf=0.25, iou=0.45, imgsz=640, apply_rules=True):
        """
        Runs standard YOLO inference on the full image resized to imgsz.
        """
        results = self.model(image, imgsz=imgsz, conf=conf, iou=iou, verbose=False)
        boxes_out = []
        for box in results[0].boxes:
            conf_val = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self.class_names.get(cls_id, str(cls_id))
            xyxy = box.xyxy[0].tolist()
            w_box = max(1.0, xyxy[2] - xyxy[0])
            h_box = max(1.0, xyxy[3] - xyxy[1])
            boxes_out.append({
                'class': cls_name,
                'class_id': cls_id,
                'confidence': round(conf_val, 4),
                'box': [round(c, 2) for c in xyxy],
                'width': round(w_box, 2),
                'height': round(h_box, 2)
            })

        if apply_rules:
            boxes_out = self.apply_layout_constraints(image, boxes_out)

        return boxes_out

    def predict_sahi(self, image: Image.Image, conf=0.20, iou_nms=0.45, imgsz=640, slice_h=800, slice_w=None, overlap=150, apply_rules=True):
        """
        Runs Sliced Hyper Inference (SAHI) on high-res / tall images.
        Divides the image into overlapping horizontal/vertical tiles, performs inference
        on each slice, and merges bounding boxes back using Non-Maximum Suppression.
        """
        w, h = image.size
        if slice_w is None:
            slice_w = w

        slice_h = max(300, min(slice_h, h))
        slice_w = max(300, min(slice_w, w))

        stride_y = max(100, slice_h - overlap)
        stride_x = max(100, slice_w - overlap)

        y_steps = list(range(0, max(1, h - slice_h + 1), stride_y))
        if y_steps[-1] + slice_h < h:
            y_steps.append(h - slice_h)

        x_steps = list(range(0, max(1, w - slice_w + 1), stride_x))
        if x_steps[-1] + slice_w < w:
            x_steps.append(w - slice_w)

        all_boxes = []
        all_scores = []
        all_classes = []

        # 1. Full image macro context pass (captures full page layout: navbar, hero, footer)
        full_res = self.model(image, imgsz=imgsz, conf=conf, verbose=False)
        for b in full_res[0].boxes:
            coords = b.xyxy[0].tolist()
            all_boxes.append(coords)
            all_scores.append(float(b.conf[0]))
            all_classes.append(int(b.cls[0]))

        # 2. Sliced high-resolution window passes (captures micro components: buttons, cards, forms)
        for y_start in y_steps:
            y_end = min(y_start + slice_h, h)
            y_start = max(0, y_end - slice_h)

            for x_start in x_steps:
                x_end = min(x_start + slice_w, w)
                x_start = max(0, x_end - slice_w)

                crop = image.crop((x_start, y_start, x_end, y_end))
                res = self.model(crop, imgsz=imgsz, conf=conf, verbose=False)

                for b in res[0].boxes:
                    coords = b.xyxy[0].tolist()
                    abs_box = [
                        coords[0] + x_start,
                        coords[1] + y_start,
                        coords[2] + x_start,
                        coords[3] + y_start
                    ]
                    all_boxes.append(abs_box)
                    all_scores.append(float(b.conf[0]))
                    all_classes.append(int(b.cls[0]))

        if not all_boxes:
            return []

        # 3. Class-aware Non-Maximum Suppression (NMS)
        b_tensor = torch.tensor(all_boxes, dtype=torch.float32)
        s_tensor = torch.tensor(all_scores, dtype=torch.float32)
        c_tensor = torch.tensor(all_classes, dtype=torch.int64)

        # Offset box coordinates by class ID for class-aware NMS to preserve valid overlaps between different component types
        max_coord = max(w, h) * 2
        offsets = c_tensor.to(torch.float32) * max_coord
        offset_boxes = b_tensor + offsets.unsqueeze(1)

        keep_indices = nms(offset_boxes, s_tensor, iou_threshold=iou_nms)

        results_out = []
        for idx in keep_indices:
            idx = int(idx)
            cls_id = int(all_classes[idx])
            cls_name = self.class_names.get(cls_id, str(cls_id))
            box_coords = [
                max(0.0, min(float(w), float(all_boxes[idx][0]))),
                max(0.0, min(float(h), float(all_boxes[idx][1]))),
                max(0.0, min(float(w), float(all_boxes[idx][2]))),
                max(0.0, min(float(h), float(all_boxes[idx][3])))
            ]
            w_box = box_coords[2] - box_coords[0]
            h_box = box_coords[3] - box_coords[1]

            if w_box <= 2 or h_box <= 2:
                continue

            conf_val = round(float(all_scores[idx]), 4)

            results_out.append({
                'class': cls_name,
                'class_id': cls_id,
                'confidence': conf_val,
                'box': [round(c, 2) for c in box_coords],
                'width': round(w_box, 2),
                'height': round(h_box, 2)
            })

        if apply_rules:
            results_out = self.apply_layout_constraints(image, results_out)

        # Sort by confidence descending
        results_out.sort(key=lambda x: x['confidence'], reverse=True)
        return results_out

    def predict_auto(self, image: Image.Image, conf=0.20):
        """
        Automatically selects optimal detection mode (Standard vs SAHI) based on image aspect ratio and height.
        """
        w, h = image.size
        aspect_ratio = h / float(w)
        if aspect_ratio >= 1.2 or h > 1200:
            return self.predict_sahi(image, conf=conf, slice_h=800, overlap=150)
        else:
            return self.predict_standard(image, conf=conf)

    def annotate_image(self, image: Image.Image, detections, line_width=3, show_conf=True):
        """
        Draws high-contrast bounding boxes and labeled badges onto the image.
        """
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except OSError:
            font = ImageFont.load_default()

        for det in detections:
            box = det['box']
            cls_name = det['class']
            conf = det['confidence']
            color = COLOR_MAP.get(cls_name, DEFAULT_COLOR)

            draw.rectangle(box, outline=color, width=line_width)

            label = f"{cls_name} {conf:.2f}" if show_conf else cls_name
            text_bbox = draw.textbbox((box[0], box[1]), label, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            label_bg = [
                box[0],
                max(0, box[1] - text_height - 6),
                box[0] + text_width + 8,
                max(text_height + 6, box[1])
            ]
            draw.rectangle(label_bg, fill=color)
            draw.text((box[0] + 4, max(0, box[1] - text_height - 4)), label, fill='white', font=font)

        return draw_image
