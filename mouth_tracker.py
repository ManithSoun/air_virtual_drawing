import cv2
import mediapipe as mp
import numpy as np
from enum import Enum, auto


class MouthLandmark(Enum):
    """Enum for specific mouth landmarks"""
    MOUTH_LEFT_CORNER = 308
    MOUTH_RIGHT_CORNER = 78
    MOUTH_CENTER_TOP = 0
    MOUTH_CENTER_BOTTOM = 17


class MouthTracker:
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.7):
        """
        Initialize MediaPipe Face Mesh for mouth tracking.

        :param detection_confidence: Minimum confidence for face detection
        :param tracking_confidence: Minimum confidence for face tracking
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def detect_mouth(self, image, draw=True):
    #Detect mouth landmarks in the image.

        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and find face mesh
        self.results = self.face_mesh.process(rgb_image)

        mouth_landmarks = []

        # Draw and extract mouth landmarks if face is detected
        if self.results.multi_face_landmarks:
            for face_landmarks in self.results.multi_face_landmarks:
                # Extract specific mouth landmarks
                height, width, _ = image.shape
                mouth_landmarks = [
                    (int(face_landmarks.landmark[idx].x * width),
                     int(face_landmarks.landmark[idx].y * height))
                    for idx in [308, 78, 0, 17]  # Left corner, right corner, top center, bottom center
                ]

                if draw:
                    # Draw mouth landmarks
                    for landmark in mouth_landmarks:
                        cv2.circle(image, landmark, 5, (0, 255, 0), -1)

        return image, mouth_landmarks

    def detect_mouth_open(self, image):
       #Detect if mouth is open by calculating vertical mouth distance.


        _, mouth_landmarks = self.detect_mouth(image, draw=False)

        if len(mouth_landmarks) >= 4:
            # Calculate vertical distance between mouth top and bottom
            mouth_height = abs(mouth_landmarks[2][1] - mouth_landmarks[3][1])

            # Calculate mouth width
            mouth_width = abs(mouth_landmarks[0][0] - mouth_landmarks[1][0])

            # Threshold for mouth open (adjust as needed)
            return mouth_height > mouth_width * 0.3

        return False