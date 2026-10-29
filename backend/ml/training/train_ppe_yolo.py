"""
Training and Fine-Tuning Script: YOLOv8 PPE Detector
Target classes: Hardhat, Safety Vest, Gloves, Goggles, Safety Boots, NO-Hardhat, NO-Safety Vest
"""

import os
from ultralytics import YOLO

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_yolo_ppe(data_yaml_path="ppe_dataset.yaml", epochs=30, img_size=640):
    print("=" * 60)
    print("YOLOv8 PPE SAFETY DETECTION FINE-TUNING PIPELINE")
    print("=" * 60)

    # If dataset yaml does not exist, prepare a demonstration structure
    if not os.path.exists(data_yaml_path):
        print(f"Dataset config '{data_yaml_path}' not found.")
        print("Creating default YOLO dataset configuration for coal mine PPE classes...")
        yaml_content = """# Coal Mine PPE Dataset Config
path: ./datasets/ppe
train: images/train
val: images/val
test: images/test

names:
  0: Hardhat
  1: Safety Vest
  2: Gloves
  3: Goggles
  4: Safety Boots
  5: NO-Hardhat
  6: NO-Safety Vest
"""
        with open(data_yaml_path, "w") as f:
            f.write(yaml_content)
        print(f"Created template at {data_yaml_path}")

    # Initialize YOLOv8 Nano base model
    model = YOLO("yolov8n.pt")
    print("Loaded base YOLOv8n weights.")
    print(f"Ready to train on {data_yaml_path} for {epochs} epochs at image size {img_size}x{img_size}.")
    print("To execute training with annotated images: yolo detect train data=ppe_dataset.yaml model=yolov8n.pt epochs=30")

if __name__ == "__main__":
    train_yolo_ppe()

