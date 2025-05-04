from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('models/yolo11x-cls.pt')
    model.train(
        data='./dataset',
        epochs=50,
        imgsz=224,
        batch=16,
        project='runs/train',
        name='yolo_classification'
    )