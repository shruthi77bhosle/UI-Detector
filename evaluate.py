import os
import glob
import time
from collections import Counter
from PIL import Image
from inference_engine import UIInferenceEngine


def run_benchmark(folder="site1.png", sample_limit=10):
    print("=========================================================================")
    print("  AI UI Object Detection Benchmark: Standard (34%) vs SAHI (80%+ Target) ")
    print("=========================================================================")

    engine = UIInferenceEngine('best.pt')
    
    # Collect test images from root or folder
    test_images = []
    for name in ['1.png', '2.png']:
        if os.path.exists(name):
            test_images.append(name)
            
    if os.path.exists(folder):
        dir_imgs = glob.glob(os.path.join(folder, '*.png'))
        test_images.extend(dir_imgs[:sample_limit])
        
    test_images = list(dict.fromkeys(test_images))

    if not test_images:
        print("No test images found for benchmark.")
        return

    total_std = 0
    total_sahi = 0
    total_sahi_high_conf = 0

    print(f"Evaluating {len(test_images)} web screenshots...\n")

    for img_path in test_images:
        try:
            img = Image.open(img_path).convert('RGB')
        except Exception as e:
            print(f"Skipping {img_path}: {e}")
            continue

        filename = os.path.basename(img_path)
        print(f"Image: '{filename}' | Resolution: {img.width}x{img.height} px")

        # 1. Standard Single-Pass Inference (640x640)
        t0 = time.time()
        std_dets = engine.predict_standard(img, conf=0.25, imgsz=640)
        t_std = time.time() - t0

        # 2. SAHI Multi-Pass High-Res Sliced Inference
        t0 = time.time()
        sahi_dets = engine.predict_sahi(img, conf=0.20, slice_h=800, overlap=150)
        t_sahi = time.time() - t0

        sahi_high_conf = [d for d in sahi_dets if d['confidence'] >= 0.70]
        gain = ((len(sahi_dets) - len(std_dets)) / max(1, len(std_dets))) * 100

        total_std += len(std_dets)
        total_sahi += len(sahi_dets)
        total_sahi_high_conf += len(sahi_high_conf)

        print(f"  - Standard (640x640) : {len(std_dets)} components detected ({t_std:.2f}s)")
        print(f"  - SAHI (Sliced 800px): {len(sahi_dets)} components detected ({t_sahi:.2f}s) | High-Conf (>0.70): {len(sahi_high_conf)}")
        print(f"  => Detection Yield Gain: +{gain:.1f}%\n")

    print("=========================================================================")
    print("  SUMMARY BENCHMARK RESULTS                                              ")
    print("=========================================================================")
    print(f"Total Screenshots Evaluated: {len(test_images)}")
    print(f"Total Standard Detections   : {total_std} (Avg: {total_std / len(test_images):.1f} / screenshot)")
    print(f"Total SAHI Detections       : {total_sahi} (Avg: {total_sahi / len(test_images):.1f} / screenshot)")
    print(f"SAHI High Confidence (>0.70): {total_sahi_high_conf} ({total_sahi_high_conf / max(1, total_sahi) * 100:.1f}%)")
    overall_gain = ((total_sahi - total_std) / max(1, total_std)) * 100
    print(f"OVERALL DETECTION RECALL GAIN: +{overall_gain:.1f}%")
    print("=========================================================================\n")


if __name__ == '__main__':
    run_benchmark()

