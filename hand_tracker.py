import cv2
import mediapipe as mp
import numpy as np
from enum import Enum, auto


class HandLandmark(Enum):
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
    THUMB_MCP = 1
    THUMB_PIP = 2
    THUMB_DIP = 3
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    # Add more landmarks as needed


class EnhancedHandTracker:
    def __init__(self, mode=False, max_hands=2, detection_confidence=0.7, tracking_confidence=0.7):
       # Initialize MediaPipe Hands tracking with enhanced configuration.
        self.mode = mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        # MediaPipe hands solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

# Detect hands in the image.
    def detect_hands(self, image, draw=True):
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and find hands
        self.results = self.hands.process(rgb_image)

        # Draw hand landmarks if requested and hands are detected
        if draw and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )

        return image

    def get_hand_landmarks(self, image, hand_index=0):
      #Get pixel coordinates of hand landmarks.
        landmarks = []
        height, width, _ = image.shape

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[hand_index]

            for landmark in hand_landmarks.landmark:
                # Convert normalized coordinates to pixel coordinates
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                landmarks.append((x, y))

        return landmarks

    def detect_gesture(self, image):
    #Detect hand gestures based on finger positions.
        landmarks = self.get_hand_landmarks(image)

        if len(landmarks) < 21:
            return []

        # Finger up detection logic
        fingers_up = []

        # Thumb special case (different orientation)
        if landmarks[HandLandmark.THUMB_TIP.value][0] < landmarks[HandLandmark.THUMB_MCP.value][0]:
            fingers_up.append(True)
        else:
            fingers_up.append(False)

        # Other fingers
        fingertip_landmarks = [
            HandLandmark.INDEX_TIP.value,
            HandLandmark.MIDDLE_TIP.value,
            HandLandmark.RING_TIP.value,
            HandLandmark.PINKY_TIP.value
        ]

        for tip, pip in zip(fingertip_landmarks, [6, 10, 14, 18]):
            if landmarks[tip][1] < landmarks[pip][1]:
                fingers_up.append(True)
            else:
                fingers_up.append(False)

        return fingers_up

    def get_pointing_finger(self, image):
     #Get the position of the pointing finger (index finger tip).

        landmarks = self.get_hand_landmarks(image)

        if len(landmarks) >= 8:
            return landmarks[HandLandmark.INDEX_TIP.value]

        return None