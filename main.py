import cv2
import numpy as np
import os
from datetime import datetime
from hand_tracker import EnhancedHandTracker
from mouth_tracker import MouthTracker
from painter import PainterUI


def create_save_directory():
    # Create a directory for saving drawings if it doesn't exist.
    save_dir = os.path.join(os.path.expanduser('~'), 'VirtualPainterSaves')
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def main():
    # Camera and application settings
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)  # Width
    cap.set(4, 720)  # Height

    # Initialize hand tracker and mouth tracker
    hand_tracker = EnhancedHandTracker(detection_confidence=0.6, tracking_confidence=0.6)
    mouth_tracker = MouthTracker(detection_confidence=0.5, tracking_confidence=0.5)

    # Initialize painter UI
    painter_ui = PainterUI()

    # Drawing canvas initialization
    canvas = np.zeros((720, 1280, 3), dtype=np.uint8) + 255  # White canvas
    previous_x, previous_y = 0, 0

    # Save directory setup
    save_dir = create_save_directory()

    # Mouth save detection cooldown and tracking
    save_cooldown = 0
    SAVE_COOLDOWN_FRAMES = 60  # About 2 seconds at typical frame rates
    mouth_open_count = 0
    MOUTH_OPEN_THRESHOLD = 10  # Require multiple frames of mouth being open

    # Smoothing variables
    smooth_x, smooth_y = 0, 0
    alpha = 0.4  # Smoothing factor (lower = more smooth, but slower response)

    while True:
        # Read frame from camera
        success, frame = cap.read()
        if not success:
            break

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # Mouth tracking
        frame, mouth_landmarks = mouth_tracker.detect_mouth(frame, draw=True)

        # Debug: Print mouth landmarks
        if mouth_landmarks:
            print(f"Mouth Landmarks: {mouth_landmarks}")

        # Default to an empty list of fingers up
        fingers_up = []

        # Hand detection and gesture recognition
        frame = hand_tracker.detect_hands(frame)  # Update results first
        if hand_tracker.results and hand_tracker.results.multi_hand_landmarks:
            fingers_up = hand_tracker.detect_gesture(frame)

        # Get pointing finger position
        pointing_finger = hand_tracker.get_pointing_finger(frame)

        # Draw UI elements
        frame = painter_ui.draw_ui(frame)

        # Handle mouth save detection with improved reliability
        if save_cooldown > 0:
            save_cooldown -= 1

        # Improved mouth open detection
        is_mouth_open = mouth_tracker.detect_mouth_open(frame)

        if is_mouth_open:
            mouth_open_count += 1
            print(f"Mouth Open Count: {mouth_open_count}")  # Debug print
        else:
            mouth_open_count = 0

        # Trigger save when mouth is consistently open
        if mouth_open_count >= MOUTH_OPEN_THRESHOLD and save_cooldown == 0:
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"air_drawing_testing_{timestamp}.png"
            save_path = os.path.join(save_dir, filename)

            # Save the canvas
            cv2.imwrite(save_path, canvas)

            # Add text overlay to indicate save
            cv2.putText(frame, f"Saved: {filename}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Reset cooldown and mouth open count
            save_cooldown = SAVE_COOLDOWN_FRAMES
            mouth_open_count = 0

        # Smooth pointing finger movement
        if pointing_finger and fingers_up:
            x, y = pointing_finger

            # Exponential smoothing for cursor movement
            smooth_x = alpha * x + (1 - alpha) * smooth_x
            smooth_y = alpha * y + (1 - alpha) * smooth_y

            # Check UI interactions
            interactions = painter_ui.handle_interactions(int(smooth_x), int(smooth_y), fingers_up)

            # Clear canvas
            if interactions['clear_canvas']:
                canvas = np.zeros((720, 1280, 3), dtype=np.uint8) + 255

            # Shape drawing mode
            if interactions['shape_drawing_mode'] and painter_ui.shape_start_point:
                # Create a copy of the canvas to draw preview
                preview_canvas = canvas.copy()
                canvas = painter_ui.draw_shape(preview_canvas,
                                               painter_ui.shape_start_point,
                                               (int(smooth_x), int(smooth_y)))

            # Drawing mode (line drawing) with smoothing
            elif interactions['drawing_mode'] and (previous_x, previous_y) != (0, 0):
                cv2.line(
                    canvas,
                    (int(previous_x), int(previous_y)),
                    (int(smooth_x), int(smooth_y)),
                    painter_ui.current_color,
                    painter_ui.current_brush_size
                )

            # Update previous coordinates
            previous_x, previous_y = int(smooth_x), int(smooth_y)
        else:
            # Reset previous coordinates when finger is not pointing
            previous_x, previous_y = 0, 0

        # Combine canvas with frame
        frame[120:, 50:1230] = cv2.addWeighted(frame[120:, 50:1230], 0.5, canvas[120:, 50:1230], 0.5, 0)

        # Display some help text
        cv2.putText(frame, "Open mouth to save drawing", (850, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow("Air Virtual Drawing (Mouth Save)", frame)

        # Exit condition
        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):  # ESC or 'q' key
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
