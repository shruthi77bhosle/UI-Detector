import os
import argparse
from ultralytics import YOLO

def train_ui_model(
    data_yaml="data.yaml",
    model_name="yolov8m.pt",  # Upgraded from yolov8n to yolov8m (25.9M parameters) for 80%+ mAP
    epochs=150,
    imgsz=1024,               # High resolution training
    batch=8,
    device="",
    project="ui_detection_runs",
    name="yolov8m_ui_high_acc"
):
    """
    Fine-tunes a medium/large YOLO model on UI Component Datasets with
    hyperparameters optimized for web interface components.
    """
    print("=================================================================")
    print(f"  Training UI Object Detection Model: {model_name}")
    print(f"  Target Resolution: {imgsz}x{imgsz} | Epochs: {epochs}")
    print("=================================================================")

    if not os.path.exists(data_yaml):
        print(f"Error: {data_yaml} not found. Please specify a valid data.yaml file.")
        return

    # Load pre-trained weights
    model = YOLO(model_name)

    # Train with UI-optimized hyperparameters
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        device=device,
        project=project,
        name=name,
        optimizer='AdamW',
        lr0=0.001,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3.0,
        box=7.5,
        cls=1.5,
        dfl=1.5,
        mosaic=1.0,
        mixup=0.15,
        scale=0.5,
        degrees=0.0,         # UI elements are non-rotated
        fliplr=0.5,          # Horizontal flip for symmetrical UI layouts
        flipud=0.0,          # Web pages are top-to-bottom
        close_mosaic=10,
        patience=30,
        save=True,
        plots=True,
        verbose=True
    )

    print("\nTraining Complete!")
    print(f"Best model weights saved to: {project}/{name}/weights/best.pt")
    return results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train UI Component Detection Model")
    parser.add_argument("--data", type=str, default="data.yaml", help="Path to data.yaml dataset config")
    parser.add_argument("--model", type=str, default="yolov8m.pt", help="Base model architecture (yolov8m.pt, yolov8l.pt, yolo11m.pt)")
    parser.add_argument("--epochs", type=int, default=150, help="Number of training epochs")
    parser.add_argument("--imgsz", type=int, default=1024, help="Training image resolution")
    parser.add_argument("--batch", type=int, default=8, help="Batch size")
    args = parser.parse_args()

    train_ui_model(
        data_yaml=args.data,
        model_name=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch
    )
