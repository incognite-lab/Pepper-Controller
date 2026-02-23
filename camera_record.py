import depthai as dai
import cv2

pipeline = dai.Pipeline()

# Create nodes
cam_rgb = pipeline.createColorCamera()
xout_rgb = pipeline.createXLinkOut()

xout_rgb.setStreamName("rgb")

cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)

cam_rgb.preview.link(xout_rgb.input)

with dai.Device(pipeline) as device:
    q_rgb = device.getOutputQueue("rgb")

    while True:
        frame = q_rgb.get().getCvFrame()
        cv2.imshow("OAK-D Pro RGB", frame)

        if cv2.waitKey(1) == ord('q'):
            break

cv2.destroyAllWindows()