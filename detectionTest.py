#################################
# name: josh ramachandran
# date: 4/12/2025
# desc: face detection program using Haar cascades
#################################

import cv2
import numpy as np
import time

# Load YOLO model configuration and weights
import os

cfg_path = 'Face_rec/yolov4-tiny.cfg'
weights_path = 'Face_rec/yolov4-tiny.weights'

# Debug print to confirm file existence
print("Checking files...")
print("Config exists:", os.path.exists(cfg_path))
print("Weights exist:", os.path.exists(weights_path))

# Load YOLO network
net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)
# Load class labels (from coco.names)
with open('Face_rec/coco.names', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

def detect_people(frame):
    # Flip the frame 180 degrees (if needed)
    frame = cv2.flip(frame, -1)

    # Prepare the image for YOLO (convert to blob)
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

    # Set the blob as input to the network
    net.setInput(blob)

    # Get the output layer names
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    # Run forward pass to get detections
    detections = net.forward(output_layers)

    height, width, _ = frame.shape
    person_count = 0

    # Loop through all detections
    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Only consider detections with high confidence
            if confidence > 0.5:
                # Check if the detected object is a "person" (class_id == 0 in coco.names)
                if classes[class_id] == "person":
                    person_count += 1

    # Return the number of people detected
    return person_count
