import os
from handwrite import converters


def generate_handwritten_notes(input_file, output_file):
    font_path = "Caveat-Regular.ttf"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    try:
        with open(input_file, "r") as f:
            full_text = f.read()

        # 6968 characters is too much for one 'page' in this library.
        # Let's try just the first 1000 characters to test the limit.
        test_chunk = full_text[:1000]

        # Save a temporary smaller file
        with open("temp_chunk.txt", "w") as f:
            f.write(test_chunk)

        print(f"Attempting to render a 1000-character chunk...")

        # Use the smaller file
        converters("temp_chunk.txt", output_file, font_path)

        print(f"Success! Check {output_file}")

    except Exception as e:
        print(f"Chunk render failed: {e}")


if __name__ == "__main__":
    generate_handwritten_notes("main.txt", "handwritten_notes.pdf")
