import os
import subprocess
import sys

# Script to generate images from all PlantUML files in a folder using the best available format
# Usage: python generate_attack_tree_image.py [input_dir] [output_dir]

BEST_FORMATS = ["svg", "png"]  # SVG is preferred for quality, PNG as fallback
PLANTUML_JAR = r"C:\Users\tuan2.pham\.vscode\extensions\jebbs.plantuml-2.18.1\plantuml.jar"


def generate_image(puml_path, output_dir):
    base_name = os.path.splitext(os.path.basename(puml_path))[0]
    for fmt in BEST_FORMATS:
        out_path = os.path.join(output_dir, f"{base_name}.{fmt}")
        cmd = [
            "java", "-jar", PLANTUML_JAR,
            f"-t{fmt}",
            "-o", output_dir,
            puml_path
        ]
        try:
            print(f"Generating {fmt.upper()} for {puml_path} ...")
            subprocess.run(cmd, check=True)
            if os.path.isfile(out_path):
                print(f"Image generated: {out_path}")
                return True
        except Exception as e:
            print(f"Failed to generate {fmt.upper()} for {puml_path}: {e}")
    print(f"Failed to generate image for {puml_path} in any preferred format.")
    return False


def main():
    input_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(input_dir, "out")
    os.makedirs(output_dir, exist_ok=True)
    puml_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.puml')]
    if not puml_files:
        print(f"No .puml files found in {input_dir}")
        sys.exit(1)
    for puml in puml_files:
        generate_image(os.path.join(input_dir, puml), output_dir)


if __name__ == "__main__":
    main()
