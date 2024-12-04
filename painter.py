import cv2
import numpy as np


class UIElement:
    def __init__(self, x, y, w, h, color, text='', alpha=1.0, text_color=(255, 255, 255)):
        """
        Create a flexible UI element with drawing and interaction capabilities.

        :param x: X-coordinate of top-left corner
        :param y: Y-coordinate of top-left corner
        :param w: Width of the element
        :param h: Height of the element
        :param color: Background color (BGR)
        :param text: Text to display on the element
        :param alpha: Transparency of the element
        :param text_color: Color of the text
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.alpha = alpha
        self.text_color = text_color
        self.is_visible = True

    def draw(self, image, font_face=cv2.FONT_HERSHEY_SIMPLEX,
             font_scale=0.7, thickness=2):
        """
        Draw the UI element on the image with a modern design.

        :param image: Image to draw on
        :param font_face: OpenCV font type
        :param font_scale: Font size scale
        :param thickness: Text thickness
        :return: Modified image
        """
        if not self.is_visible:
            return image

        # Ensure ROI is within image bounds
        y_end = min(self.y + self.h, image.shape[0])
        x_end = min(self.x + self.w, image.shape[1])

        # Adjust dimensions to prevent out-of-bounds errors
        h = y_end - self.y
        w = x_end - self.x

        if h <= 0 or w <= 0:
            return image

        # Extract the region of interest
        roi = image[self.y:y_end, self.x:x_end]

        # Create a soft gradient overlay
        overlay = np.zeros(roi.shape, dtype=np.uint8)
        for i in range(h):
            # Create a gradient from darker to lighter shade of the base color
            alpha = i / h
            gradient_color = tuple(int(c * (0.5 + alpha * 0.5)) for c in self.color)
            overlay[i, :] = gradient_color

        # Blend the original image with the overlay
        blended = cv2.addWeighted(roi, self.alpha, overlay, 1 - self.alpha, 1.0)

        # Add rounded rectangle effect
        cv2.rectangle(blended, (5, 5), (w - 5, h - 5),
                      (200, 200, 200), 2)  # Highlight border
        cv2.rectangle(blended, (0, 0), (w, h),
                      (100, 100, 100), 1)  # Soft outer border

        # Put the blended region back
        image[self.y:y_end, self.x:x_end] = blended

        # Add text if present
        if self.text:
            text_size = cv2.getTextSize(self.text, font_face, font_scale, thickness)
            text_x = int(self.x + w / 2 - text_size[0][0] / 2)
            text_y = int(self.y + h / 2 + text_size[0][1] / 2)
            cv2.putText(image, self.text, (text_x, text_y),
                        font_face, font_scale, self.text_color, thickness)

        return image

    def is_over(self, x, y):
        """
        Check if a point is within the UI element.

        :param x: X-coordinate of the point
        :param y: Y-coordinate of the point
        :return: Boolean indicating if point is inside the element
        """
        return (self.x < x < self.x + self.w) and (self.y < y < self.y + self.h)


class PainterUI:
    def __init__(self, width=1280, height=720):
    #Initialize a comprehensive UI for the virtual painter with a compact design.

        self.canvas_background_color = (255, 255, 255)

        self.width = width
        self.height = height
        self.shape_y = 100  # Y-coordinate for shape buttons

        # Define a more compact UI layout
        base_x = 50  # Starting x-coordinate for buttons
        base_y = 20  # Starting y-coordinate for buttons
        button_width = 120  # Reduced button width
        button_height = 50  # Reduced button height
        horizontal_spacing = 10  # Reduced horizontal spacing between buttons
        vertical_spacing = 10  # Reduced vertical spacing between buttons

        # Curated color palette (modern, soft colors)
        color_palette = [
            (50, 120, 220),  # Soft blue
            (80, 180, 120),  # Mint green
            (230, 130, 80),  # Soft orange
            (180, 80, 180),  # Lavender purple
            (220, 90, 120),  # Soft pink
        ]

        # Utility buttons with compact, flat design (horizontally stacked)
        button_color = (100, 100, 100)
        self.toggle_buttons = [
            UIElement(
                base_x + (button_width + horizontal_spacing) * i,
                base_y,
                button_width,
                button_height,
                button_color,
                btn_text,
                1.0,
                (255, 255, 255)
            )
            for i, btn_text in enumerate(['Colors', 'Shapes', 'Pen', 'Save', 'Clear'])
        ]

        # Map buttons to their attributes or actions
        self.button_actions = {
            'Colors': 'hide_colors',
            'Shapes': 'hide_shapes',
            'Pen': 'hide_pen_sizes',
            'Save': 'save_drawing',
            'Clear': 'clear_canvas'
        }

        # Color selection UI with aligned design
        color_x = base_x
        color_y = base_y + button_height + vertical_spacing

        self.colors = [
            UIElement(
                color_x + (80 + horizontal_spacing) * i,
                color_y,
                80,
                button_height,
                color=color,
                text='',
                alpha=0.8,
                text_color=(0, 0, 0)
            )
            for i, color in enumerate(color_palette)
        ]

        # Eraser with a distinct look
        self.colors.append(
            UIElement(
                color_x + (80 + horizontal_spacing) * len(color_palette),
                color_y,
                100,
                button_height,
                color=(240, 240, 240),
                text='Eraser',
                alpha=0.8,
                text_color=(50, 50, 50)
            )
        )

        # Pen size selector with aligned design
        pen_x = base_x
        pen_y = color_y + button_height + vertical_spacing

        pen_color = (70, 70, 70)
        self.pen_sizes = [
            UIElement(
                pen_x + (button_width + horizontal_spacing) * i,
                pen_y,
                button_width,
                button_height,
                pen_color,
                str(size),
                1.0,
                (255, 255, 255)
            )
            for i, size in enumerate(range(5, 25, 5))
        ]

        # Shape selection buttons
        shape_x = base_x
        shape_y = pen_y + button_height + vertical_spacing

        shape_color = (90, 90, 90)
        self.shapes = [
            UIElement(
                shape_x + (button_width + horizontal_spacing) * i,
                shape_y,
                button_width,
                button_height,
                shape_color,
                shape,
                1.0,
                (255, 255, 255)
            )
            for i, shape in enumerate(['Circle', 'Rectangle', 'Triangle'])
        ]

        # Drawing canvas with subtle border
        self.canvas = UIElement(
            50,
            shape_y - 70,
            width - 100,
            1780,
            (240, 240, 240),
            alpha=0.8
        )

        # Additional state variables
        self.current_color = color_palette[0]  # Default soft blue
        self.current_brush_size = 5
        self.hide_colors = True
        self.hide_pen_sizes = True
        self.hide_shapes = True
        self.current_shape = None
        self.shape_start_point = None
        self.shape_drawing_mode = False

    def draw_ui(self, image):

        # Draw toggle buttons
        for btn in self.toggle_buttons:
            btn.draw(image)

        # Draw board (optional, can be toggled)
        self.canvas.draw(image)

        # Draw color palette if not hidden
        if not self.hide_colors:
            for color_btn in self.colors:
                color_btn.draw(image)

        # Draw pen sizes if not hidden
        if not self.hide_pen_sizes:
            for pen_size in self.pen_sizes:
                pen_size.draw(image)

        # Draw shape buttons if not hidden
        if not self.hide_shapes:
            for shape_btn in self.shapes:
                shape_btn.draw(image)

        return image

    def handle_interactions(self, x, y, fingers_up):
        """
        Handle user interactions with UI elements.

        :param x: X-coordinate of interaction point
        :param y: Y-coordinate of the point
        :param fingers_up: List of finger status
        :return: Dictionary of interaction results
        """
        interactions = {
            'color_changed': False,
            'brush_size_changed': False,
            'clear_canvas': False,
            'drawing_mode': False,
            'shape_drawing_mode': False,
            'save_drawing': False
        }

        # Check toggle buttons
        if fingers_up[1]:  # Index finger
            for btn in self.toggle_buttons:
                if btn.is_over(x, y):
                    action = self.button_actions.get(btn.text)

                    # Handle special actions
                    if action == 'hide_colors':
                        self.hide_colors = not self.hide_colors
                    elif action == 'hide_shapes':
                        self.hide_shapes = not self.hide_shapes
                    elif action == 'hide_pen_sizes':
                        self.hide_pen_sizes = not self.hide_pen_sizes
                    elif action == 'clear_canvas':
                        interactions['clear_canvas'] = True
                    elif action == 'save_drawing':
                        interactions['save_drawing'] = True
                    break

        # Color selection
        if not self.hide_colors and fingers_up[1]:
            for color_btn in self.colors:
                if color_btn.is_over(x, y):
                    if color_btn.text == "Eraser":
                        self.current_color = self.canvas_background_color  # Set color to canvas background
                        self.current_brush_size = 20  # Set a larger size for eraser
                    else:
                        self.current_color = color_btn.color
                        self.current_brush_size = 5
                    interactions['color_changed'] = True
                    break

        # Pen size selection
        if not self.hide_pen_sizes and fingers_up[1]:
            for pen_size_btn in self.pen_sizes:
                if pen_size_btn.is_over(x, y):
                    self.current_brush_size = int(pen_size_btn.text)
                    interactions['brush_size_changed'] = True
                    break

        # Shape selection
        if not self.hide_shapes and fingers_up[1]:
            for shape_btn in self.shapes:
                if shape_btn.is_over(x, y):
                    self.current_shape = shape_btn.text
                    self.shape_drawing_mode = False
                    break

        # Drawing mode
        if self.canvas.is_over(x, y):
            # Check if only index finger is up
            if fingers_up[1] and not fingers_up[0]:
                interactions['drawing_mode'] = True

        # Shape drawing mode
        if self.canvas.is_over(x, y):
            # Shape drawing logic (only when a shape is selected and index finger is down)
            if not self.hide_shapes and self.current_shape:
                # Start drawing when first detecting the point
                if not self.shape_drawing_mode and fingers_up[0]:
                    self.shape_start_point = (x, y)
                    self.shape_drawing_mode = True
                    interactions['shape_drawing_mode'] = True
                elif self.shape_drawing_mode and not fingers_up[0]:
                    # End drawing and reset
                    self.shape_drawing_mode = False
                    self.current_shape = None

        return interactions

    def draw_shape(self, canvas, start_point, end_point):
        """
        Draw selected shape on the canvas.

        :param canvas: Canvas to draw on
        :param start_point: Starting point of shape
        :param end_point: Ending point of shape
        :return: Updated canvas
        """
        # Calculate dimensions
        x1, y1 = start_point
        x2, y2 = end_point
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        if self.current_shape == 'Circle':
            # Draw circle with center at start point and radius based on width/height
            center = (x1, y1)
            radius = int(min(width, height) / 2)
            cv2.circle(canvas, center, radius, self.current_color, self.current_brush_size)

        elif self.current_shape == 'Rectangle':
            # Draw rectangle using two points
            cv2.rectangle(canvas, start_point, end_point, self.current_color, self.current_brush_size)

        elif self.current_shape == 'Triangle':
            # Calculate triangle points
            points = np.array([
                [x1, y2],  # Bottom left
                [x2, y2],  # Bottom right
                [(x1 + x2) // 2, y1]  # Top middle
            ], np.int32)
            cv2.polylines(canvas, [points], True, self.current_color, self.current_brush_size)

        return canvas