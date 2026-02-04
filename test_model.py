from ultralytics import YOLO

model = YOLO('best.pt')
results=model.predict(source='test.jpg',conf=0.5,save=True)

for result in results:
    for box in result.boxes:
        class_id=int(box.cls[0])
        class_name=model.names[class_id]
        confidence=float(box.conf[0])

        print(f'\n find {class_name}(confidence: {confidence:.2f})')
    print('\n test complete')