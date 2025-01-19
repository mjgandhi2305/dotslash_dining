from flask import Flask, render_template, Response
import cv2
from pyzbar.pyzbar import decode
import numpy as np

app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(3, 640)  # Set width
camera.set(4, 480)  # Set height

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            for barcode in decode(frame):
                qr_data = barcode.data.decode('utf-8')
                qr_type = barcode.type
                print(f"QR Code Type: {qr_type}")
                print(f"QR Code Data: {qr_data}")
                
                points = barcode.polygon
                if len(points) == 4:
                    pts = [(point.x, point.y) for point in points]
                    pts = np.array(pts, dtype=np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
                
                cv2.putText(frame, qr_data, (barcode.rect.left, barcode.rect.top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
    