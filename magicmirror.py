import cv2
import base64
import requests
import pygame
import sys

# Capture an image from the webcam
def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return None

    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Error: Could not read frame")
        return None

    # Save the image
    img_path = 'captured_image.jpg'
    cv2.imwrite(img_path, frame)
    return img_path

# Encode image to base64
def encode_image_to_base64(img_path):
    with open(img_path, 'rb') as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
    return encoded_image

# Send image to Claude API and get a positive message
def get_positive_message(encoded_image):
    url = "https://api.anthropic.com/v1/messages"
    api_key = "[CLAUDE API KEY]"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    payload = {
        "model": "claude-3-sonnet-20240229",  # Use the sonnet model
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": encoded_image
                        }
                    },
                    {
                        "type": "text",
                        "text": "Generate a positive message for the person in this image. Do not output anything other than a positive message for the person in the image. If there is no human in the image, please output 'It's indeed a good day, but I see no human out here'. Do not output/say things like:  I apologize, but I cannot identify specific individuals in images to protect their privacy. Because nobody is asking to identify them. You just have the picture of a person and you have to generate a positive message for them. Each message for every distinct person should be unique."
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        message = response.json()["content"][0]["text"]
        return message
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None

# Wrap text to fit within the screen width
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        if font.size(' '.join(current_line))[0] > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]

    lines.append(' '.join(current_line))
    return lines

# Display animated text
def display_message(message):
    pygame.init()

    # Set up the display
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Positive Message')

    # Define colors
    peach_gradient = [(255, 218, 185), (255, 203, 164)]

    # Define text properties
    font = pygame.font.SysFont('Arial', 48)
    text_color = (0, 0, 0)

    # Gradient background function
    def draw_gradient():
        for y in range(height):
            color = [
                peach_gradient[0][i] + (peach_gradient[1][i] - peach_gradient[0][i]) * y // height
                for i in range(3)
            ]
            pygame.draw.line(screen, color, (0, y), (width, y))

    # Wrap and render the text
    max_width = width - 40  # margin
    wrapped_lines = wrap_text(message, font, max_width)
    line_height = font.get_linesize()
    total_height = line_height * len(wrapped_lines)

    # Animation variables
    alpha = 0
    increment = 5
    scroll_speed = 1
    y_offset = height

    text_surfaces = [font.render(line, True, text_color) for line in wrapped_lines]

    clock = pygame.time.Clock()
    fade_in_complete = False
    scroll_complete = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Draw gradient background
        draw_gradient()

        # Animate text
        if not fade_in_complete:
            if alpha < 255:
                alpha += increment
            else:
                fade_in_complete = True
        else:
            if y_offset + total_height > 0:
                y_offset -= scroll_speed
            else:
                scroll_complete = True

        for idx, surface in enumerate(text_surfaces):
            surface.set_alpha(alpha)
            screen.blit(surface, ((width - surface.get_width()) // 2, y_offset + idx * line_height))

        pygame.display.update()
        clock.tick(30)

        if scroll_complete:
            break

def main():
    img_path = capture_image()
    if img_path:
        encoded_image = encode_image_to_base64(img_path)
        positive_message = get_positive_message(encoded_image)
        if positive_message:
            display_message(positive_message)

if __name__ == "__main__":
    main()
