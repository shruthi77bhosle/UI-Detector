import io
from collections import Counter
from flask import Flask, request, jsonify
from PIL import Image
from inference_engine import UIInferenceEngine

app = Flask(__name__)
engine = UIInferenceEngine('best.pt')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'online',
        'model': 'YOLOv8-UI-Detector',
        'classes': list(engine.class_names.values()),
        'sahi_supported': True
    })


@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded in request'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Empty filename uploaded'}), 400

    # Parse options
    use_sahi = request.args.get('use_sahi', 'true').lower() == 'true'
    conf = float(request.args.get('conf', 0.25))
    iou = float(request.args.get('iou', 0.45))
    imgsz = int(request.args.get('imgsz', 640))
    slice_h = int(request.args.get('slice_h', 800))
    overlap = int(request.args.get('overlap', 150))

    try:
        img = Image.open(io.BytesIO(file.read())).convert('RGB')
    except Exception as e:
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 400

    if use_sahi:
        detections = engine.predict_sahi(
            img,
            conf=conf,
            iou_nms=iou,
            imgsz=imgsz,
            slice_h=slice_h,
            overlap=overlap
        )
        mode = 'SAHI Sliced Inference'
    else:
        detections = engine.predict_standard(
            img,
            conf=conf,
            iou=iou,
            imgsz=imgsz
        )
        mode = 'Standard Resized Inference'

    breakdown = dict(Counter(d['class'] for d in detections))

    return jsonify({
        'success': True,
        'mode': mode,
        'image_size': {'width': img.width, 'height': img.height},
        'total_detections': len(detections),
        'breakdown': breakdown,
        'detections': detections
    })


if __name__ == '__main__':
    print("Starting UI Component Detection API Server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)