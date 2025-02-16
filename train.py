from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('models/yolo11n-cls.pt')
    model.train(
        data='./dataset',
        epochs=50,
        imgsz=1024,
        batch=16,
        project='runs/train',
        name='yolo_classification'
    )