import os
import glob
import random
import shutil
import yaml
from PIL import Image, ImageDraw, ImageFont


CLASSES = ['button', 'card', 'contact_form', 'footer', 'hero', 'navbar']


def generate_synthetic_web_layout(output_img_path, output_label_path, width=1366, height=3500):
    """
    Generates a realistic synthetic web page layout screenshot and creates
    matching ground-truth YOLO labels with balanced UI components.
    """
    img = Image.new('RGB', (width, height), color='#0F172A')
    draw = ImageDraw.Draw(img)

    labels = []

    # 1. Navbar (Top of page)
    nav_h = random.randint(60, 90)
    nav_box = [0, 0, width, nav_h]
    draw.rectangle(nav_box, fill='#1E293B')
    draw.text((20, nav_h // 3), "BRAND LOGO", fill='#38BDF8')

    # Add 2-3 buttons in navbar
    for b in range(random.randint(2, 4)):
        btn_w = random.randint(80, 120)
        btn_x1 = width - (b + 1) * (btn_w + 15) - 30
        btn_y1 = (nav_h - 36) // 2
        btn_x2 = btn_x1 + btn_w
        btn_y2 = btn_y1 + 36
        draw.rectangle([btn_x1, btn_y1, btn_x2, btn_y2], fill='#3B82F6')
        draw.text((btn_x1 + 10, btn_y1 + 8), "Nav Btn", fill='white')
        # Button label
        labels.append((0, (btn_x1 + btn_x2) / 2 / width, (btn_y1 + btn_y2) / 2 / height, (btn_x2 - btn_x1) / width, (btn_y2 - btn_y1) / height))

    # Navbar label (Class 5)
    labels.append((5, (nav_box[0] + nav_box[2]) / 2 / width, (nav_box[1] + nav_box[3]) / 2 / height, (nav_box[2] - nav_box[0]) / width, (nav_box[3] - nav_box[1]) / height))

    current_y = nav_h + 10

    # 2. Hero Section (Class 4)
    hero_h = random.randint(450, 650)
    hero_box = [0, current_y, width, current_y + hero_h]
    draw.rectangle(hero_box, fill='#1E1E38')
    draw.text((width // 4, current_y + 80), "HERO HEADLINE TITLE", fill='#F8FAFC')

    # Hero CTA buttons
    for b in range(2):
        btn_w = 140
        btn_h = 44
        btn_x1 = width // 4 + b * 160
        btn_y1 = current_y + 220
        btn_x2 = btn_x1 + btn_w
        btn_y2 = btn_y1 + btn_h
        draw.rectangle([btn_x1, btn_y1, btn_x2, btn_y2], fill='#F97316' if b == 0 else '#475569')
        draw.text((btn_x1 + 20, btn_y1 + 12), "Get Started" if b == 0 else "Learn More", fill='white')
        labels.append((0, (btn_x1 + btn_x2) / 2 / width, (btn_y1 + btn_y2) / 2 / height, btn_w / width, btn_h / height))

    labels.append((4, (hero_box[0] + hero_box[2]) / 2 / width, (hero_box[1] + hero_box[3]) / 2 / height, (hero_box[2] - hero_box[0]) / width, hero_h / height))

    current_y += hero_h + 40

    # 3. Cards Section (Class 1)
    num_card_rows = random.randint(2, 4)
    for row in range(num_card_rows):
        cards_per_row = random.choice([2, 3, 4])
        margin = 40
        card_w = (width - margin * (cards_per_row + 1)) // cards_per_row
        card_h = random.randint(300, 420)

        for col in range(cards_per_row):
            cx1 = margin + col * (card_w + margin)
            cy1 = current_y
            cx2 = cx1 + card_w
            cy2 = cy1 + card_h
            draw.rectangle([cx1, cy1, cx2, cy2], fill='#334155', outline='#475569', width=2)
            draw.text((cx1 + 20, cy1 + 20), f"Card Title {row*cards_per_row + col + 1}", fill='#F1F5F9')

            # Card action button
            btn_w = 110
            btn_h = 36
            bx1 = cx1 + 20
            by1 = cy2 - 50
            bx2 = bx1 + btn_w
            by2 = by1 + btn_h
            draw.rectangle([bx1, by1, bx2, by2], fill='#10B981')
            draw.text((bx1 + 15, by1 + 8), "View Details", fill='white')
            labels.append((0, (bx1 + bx2) / 2 / width, (by1 + by2) / 2 / height, btn_w / width, btn_h / height))

            # Card label
            labels.append((1, (cx1 + cx2) / 2 / width, (cy1 + cy2) / 2 / height, card_w / width, card_h / height))

        current_y += card_h + 40

    # 4. Contact Form Section (Class 2)
    form_w = random.randint(500, 700)
    form_h = random.randint(350, 450)
    fx1 = (width - form_w) // 2
    fy1 = current_y
    fx2 = fx1 + form_w
    fy2 = fy1 + form_h
    draw.rectangle([fx1, fy1, fx2, fy2], fill='#1E293B', outline='#EAB308', width=2)
    draw.text((fx1 + 30, fy1 + 30), "Contact Us Form", fill='#EAB308')

    # Input fields
    for inp in range(2):
        ix1 = fx1 + 30
        iy1 = fy1 + 80 + inp * 60
        ix2 = fx2 - 30
        iy2 = iy1 + 40
        draw.rectangle([ix1, iy1, ix2, iy2], fill='#0F172A', outline='#64748B')

    # Form Submit Button
    sb_w = 130
    sb_h = 40
    sb_x1 = fx1 + 30
    sb_y1 = fy2 - 60
    sb_x2 = sb_x1 + sb_w
    sb_y2 = sb_y1 + sb_h
    draw.rectangle([sb_x1, sb_y1, sb_x2, sb_y2], fill='#EAB308')
    draw.text((sb_x1 + 25, sb_y1 + 10), "Submit", fill='black')
    labels.append((0, (sb_x1 + sb_x2) / 2 / width, (sb_y1 + sb_y2) / 2 / height, sb_w / width, sb_h / height))

    labels.append((2, (fx1 + fx2) / 2 / width, (fy1 + fy2) / 2 / height, form_w / width, form_h / height))

    current_y += form_h + 60

    # 5. Footer (Class 3)
    foot_h = random.randint(180, 260)
    foot_box = [0, height - foot_h, width, height]
    draw.rectangle(foot_box, fill='#090D16')
    draw.text((40, height - foot_h + 40), "© 2026 Web Application. All rights reserved.", fill='#94A3B8')

    # Footer button
    fb_x1 = width - 180
    fb_y1 = height - foot_h + 40
    fb_x2 = fb_x1 + 140
    fb_y2 = fb_y1 + 36
    draw.rectangle([fb_x1, fb_y1, fb_x2, fb_y2], fill='#EF4444')
    draw.text((fb_x1 + 15, fb_y1 + 8), "Subscribe", fill='white')
    labels.append((0, (fb_x1 + fb_x2) / 2 / width, (fb_y1 + fb_y2) / 2 / height, 140 / width, 36 / height))

    labels.append((3, (foot_box[0] + foot_box[2]) / 2 / width, (foot_box[1] + foot_box[3]) / 2 / height, (foot_box[2] - foot_box[0]) / width, foot_h / height))

    # Save image
    img.save(output_img_path)

    # Save YOLO labels
    with open(output_label_path, 'w') as f:
        for l in labels:
            f.write(f"{l[0]} {l[1]:.6f} {l[2]:.6f} {l[3]:.6f} {l[4]:.6f}\n")


def build_dataset(total_samples=210, base_dir="dataset"):
    print(f"=================================================================")
    print(f"  Building 200+ Annotated UI Dataset in '{base_dir}'...")
    print(f"=================================================================")

    train_img_dir = os.path.join(base_dir, "images", "train")
    val_img_dir = os.path.join(base_dir, "images", "val")
    train_lbl_dir = os.path.join(base_dir, "labels", "train")
    val_lbl_dir = os.path.join(base_dir, "labels", "val")

    for d in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
        os.makedirs(d, exist_ok=True)

    val_count = int(total_samples * 0.20)
    train_count = total_samples - val_count

    print(f"Generating {train_count} training samples and {val_count} validation samples...")

    for i in range(total_samples):
        is_val = i >= train_count
        target_img_dir = val_img_dir if is_val else train_img_dir
        target_lbl_dir = val_lbl_dir if is_val else train_lbl_dir

        idx_str = f"web_ui_{i+1:03d}"
        img_p = os.path.join(target_img_dir, f"{idx_str}.png")
        lbl_p = os.path.join(target_lbl_dir, f"{idx_str}.txt")

        h_val = random.randint(2800, 4500)
        generate_synthetic_web_layout(img_p, lbl_p, width=1366, height=h_val)

    # Write data.yaml
    data_yaml_content = {
        'path': os.path.abspath(base_dir),
        'train': 'images/train',
        'val': 'images/val',
        'names': {
            0: 'button',
            1: 'card',
            2: 'contact_form',
            3: 'footer',
            4: 'hero',
            5: 'navbar'
        }
    }

    yaml_path = os.path.join(base_dir, "data.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml_content, f, sort_keys=False)

    print(f"\nDataset Generation Complete!")
    print(f"  - Config Saved: {yaml_path}")
    print(f"  - Total Images: {total_samples} (Train: {train_count}, Val: {val_count})")
    print(f"  - Classes     : {CLASSES}\n")
    return yaml_path


if __name__ == '__main__':
    build_dataset(total_samples=210)
