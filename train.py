from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('yolo11n-cls', task="classify")
    model.train(
        data='./dataset',
        epochs=100,
        batch=64,
        project='runs/train',
        name='yolo_classification'
    )