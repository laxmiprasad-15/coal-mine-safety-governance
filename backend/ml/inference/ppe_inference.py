"""
Standalone PPE Inference Script for Coal Mine Safety System
Can be run independently on images/videos without the full FastAPI server.

Usage:
    python backend/ml/inference/ppe_inference.py --image path/to/image.jpg
    python backend/ml/inference/ppe_inference.py --video path/to/video.mp4
    python backend/ml/inference/ppe_inference.py --webcam
"""

import argparse
import cv2
import numpy as np
import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# PPE classes and safety rules
PPE_CLASSES = {
    'helmet': {'required': True, 'color': (0, 255, 0)},
    'safety-vest': {'required': True, 'color': (255, 165, 0)},
    'goggles': {'required': False, 'color': (0, 255, 255)},
    'gloves': {'required': False, 'color': (255, 0, 255)},
    'safety-boots': {'required': False, 'color': (0, 128, 255)},
    'person': {'required': False, 'color': (128, 128, 128)},
}

VIOLATION_MESSAGES = {
    'no_helmet': 'VIOLATION: No Helmet Detected',
    'no_vest': 'VIOLATION: No Safety Vest Detected',
    'no_goggles': 'WARNING: No Eye Protection',
}

DGMS_COLORS = {
    'safe': (22, 163, 74),      # Green
    'warning': (217, 119, 6),   # Amber
    'danger': (220, 38, 38),    # Red
}


class PPEInferenceEngine:
    """Standalone PPE detection inference engine using YOLOv8."""
    
    def __init__(self, model_path: str = None, confidence: float = 0.45):
        self.confidence = confidence
        self.model = None
        self.use_yolo = False
        
        # Try to load YOLOv8
        try:
            from ultralytics import YOLO
            if model_path and os.path.exists(model_path):
                self.model = YOLO(model_path)
                print(f"✓ Loaded custom YOLOv8 model from: {model_path}")
            else:
                self.model = YOLO('yolov8n.pt')
                print("✓ Loaded YOLOv8n pretrained model (COCO)")
            self.use_yolo = True
        except ImportError:
            print("⚠ Ultralytics not installed. Using OpenCV heuristic fallback.")
        except Exception as e:
            print(f"⚠ YOLOv8 load error: {e}. Using heuristic fallback.")
    
    def detect_ppe(self, frame: np.ndarray) -> dict:
        """
        Run PPE detection on a frame.
        
        Returns:
            {
                'violations': list of violation strings,
                'detections': list of {class, confidence, bbox},
                'risk_level': 'Safe' | 'Warning' | 'Danger',
                'annotated_frame': np.ndarray
            }
        """
        annotated = frame.copy()
        detections = []
        violations = []
        
        if self.use_yolo and self.model:
            results = self.model(frame, conf=self.confidence, verbose=False)
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
                    
                    cls_name = result.names.get(cls_id, f'class_{cls_id}').lower()
                    
                    # Map COCO classes to PPE context
                    display_name = cls_name
                    color = (200, 200, 200)
                    
                    if 'person' in cls_name:
                        color = DGMS_COLORS['warning']
                        display_name = 'Worker (no PPE check)'
                    elif 'helmet' in cls_name or 'hardhat' in cls_name:
                        color = DGMS_COLORS['safe']
                        display_name = 'Helmet ✓'
                    elif 'vest' in cls_name:
                        color = DGMS_COLORS['safe']
                        display_name = 'Safety Vest ✓'
                    
                    detections.append({
                        'class': cls_name,
                        'display_name': display_name,
                        'confidence': round(conf, 3),
                        'bbox': [x1, y1, x2, y2]
                    })
                    
                    # Draw bounding box
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                    label = f'{display_name} {conf:.0%}'
                    cv2.putText(annotated, label, (x1, y1 - 8),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        else:
            # Heuristic fallback: use color segmentation
            detections, annotated = self._heuristic_detect(frame)
        
        # Determine violations
        found_classes = {d['class'].lower() for d in detections}
        
        has_person = any('person' in c for c in found_classes)
        has_helmet = any('helmet' in c or 'hardhat' in c for c in found_classes)
        has_vest = any('vest' in c for c in found_classes)
        
        if has_person and not has_helmet:
            violations.append('Missing Helmet/Hardhat')
        if has_person and not has_vest:
            violations.append('Missing Safety Vest')
        
        # Risk level
        if not violations:
            risk_level = 'Safe'
            border_color = DGMS_COLORS['safe']
        elif len(violations) == 1:
            risk_level = 'Warning'
            border_color = DGMS_COLORS['warning']
        else:
            risk_level = 'Danger'
            border_color = DGMS_COLORS['danger']
        
        # Draw overlay header
        h, w = annotated.shape[:2]
        cv2.rectangle(annotated, (0, 0), (w, 36), (30, 30, 30), -1)
        status_text = f"Risk: {risk_level} | Violations: {len(violations)} | Detections: {len(detections)}"
        cv2.putText(annotated, status_text, (10, 24),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.55, border_color, 2)
        
        # Draw violation text
        for i, viol in enumerate(violations):
            cv2.putText(annotated, f"⚠ {viol}", (10, h - 20 - i * 22),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, DGMS_COLORS['danger'], 2)
        
        # DGMS watermark
        cv2.putText(annotated, "Coal Mine Safety - DGMS", (w - 230, h - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        return {
            'violations': violations,
            'detections': detections,
            'risk_level': risk_level,
            'annotated_frame': annotated,
            'timestamp': datetime.now().isoformat()
        }
    
    def _heuristic_detect(self, frame: np.ndarray):
        """
        Simple color-based heuristic for PPE detection.
        Uses HSV color ranges for helmet (yellow/orange) and vest (high-vis yellow/orange).
        """
        detections = []
        annotated = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # High-visibility yellow (PPE vest/helmet)
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([35, 255, 255])
        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        # Orange (PPE items)
        orange_lower = np.array([10, 100, 100])
        orange_upper = np.array([20, 255, 255])
        orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
        
        ppe_mask = cv2.bitwise_or(yellow_mask, orange_mask)
        contours, _ = cv2.findContours(ppe_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                ar = w / max(h, 1)
                
                if ar > 1.5:
                    class_name = 'safety-vest'
                else:
                    class_name = 'helmet'
                
                confidence = min(0.95, area / 5000)
                detections.append({
                    'class': class_name,
                    'display_name': f'{class_name} (heuristic)',
                    'confidence': round(confidence, 2),
                    'bbox': [x, y, x+w, y+h]
                })
                cv2.rectangle(annotated, (x, y), (x+w, y+h), DGMS_COLORS['safe'], 2)
                cv2.putText(annotated, f"{class_name} {confidence:.0%}", (x, y-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, DGMS_COLORS['safe'], 1)
        
        return detections, annotated
    
    def process_image(self, image_path: str, output_path: str = None) -> dict:
        """Process a single image file."""
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        result = self.detect_ppe(frame)
        
        if output_path:
            cv2.imwrite(output_path, result['annotated_frame'])
            print(f"✓ Annotated image saved to: {output_path}")
        
        return result
    
    def process_video(self, video_path: str, output_path: str = None, show: bool = True) -> list:
        """Process a video file frame by frame."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        results = []
        frame_count = 0
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 5th frame for performance
                if frame_count % 5 == 0:
                    result = self.detect_ppe(frame)
                    results.append({'frame': frame_count, **result})
                    
                    if show:
                        cv2.imshow('PPE Detection - Coal Mine Safety', result['annotated_frame'])
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    
                    if writer:
                        writer.write(result['annotated_frame'])
                
                frame_count += 1
        finally:
            cap.release()
            if writer:
                writer.release()
            if show:
                cv2.destroyAllWindows()
        
        return results
    
    def process_webcam(self, camera_id: int = 0):
        """Process live webcam feed."""
        print(f"Opening camera {camera_id}... Press 'q' to quit, 's' to save screenshot.")
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open camera {camera_id}")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                result = self.detect_ppe(frame)
                
                cv2.imshow('PPE Detection - Coal Mine Safety (Live)', result['annotated_frame'])
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    path = f'screenshot_ppe_{ts}.jpg'
                    cv2.imwrite(path, result['annotated_frame'])
                    print(f"Screenshot saved: {path}")
        finally:
            cap.release()
            cv2.destroyAllWindows()


def print_result(result: dict):
    """Pretty-print detection results."""
    print("\n" + "=" * 50)
    print(f"PPE Detection Result")
    print("=" * 50)
    print(f"Timestamp:   {result['timestamp']}")
    print(f"Risk Level:  {result['risk_level']}")
    print(f"Detections:  {len(result['detections'])}")
    print(f"Violations:  {len(result['violations'])}")
    
    if result['detections']:
        print("\nDetected Objects:")
        for det in result['detections']:
            print(f"  [{det['confidence']:.0%}] {det['class']} at bbox {det['bbox']}")
    
    if result['violations']:
        print("\nViolations Found:")
        for v in result['violations']:
            print(f"  ⚠  {v}")
    else:
        print("\n✓ No PPE violations detected")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='PPE Detection Inference for Coal Mine Safety',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ppe_inference.py --image worker.jpg
  python ppe_inference.py --image worker.jpg --output annotated.jpg
  python ppe_inference.py --video feed.mp4 --output annotated.mp4
  python ppe_inference.py --webcam
  python ppe_inference.py --webcam --camera 1
        """
    )
    parser.add_argument('--image', type=str, help='Path to input image')
    parser.add_argument('--video', type=str, help='Path to input video')
    parser.add_argument('--webcam', action='store_true', help='Use live webcam')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--output', type=str, help='Path to save annotated output')
    parser.add_argument('--model', type=str, help='Path to custom YOLOv8 model weights (.pt)')
    parser.add_argument('--conf', type=float, default=0.45, help='Confidence threshold (default: 0.45)')
    parser.add_argument('--no-show', action='store_true', help='Do not display window (for headless mode)')
    
    args = parser.parse_args()
    
    if not any([args.image, args.video, args.webcam]):
        parser.print_help()
        print("\nError: Specify --image, --video, or --webcam")
        sys.exit(1)
    
    print("Initializing PPE Detection Engine...")
    engine = PPEInferenceEngine(model_path=args.model, confidence=args.conf)
    
    if args.image:
        print(f"Processing image: {args.image}")
        result = engine.process_image(args.image, output_path=args.output)
        print_result(result)
        
    elif args.video:
        print(f"Processing video: {args.video}")
        results = engine.process_video(args.video, output_path=args.output, show=not args.no_show)
        print(f"\nProcessed {len(results)} frames")
        violations = sum(len(r['violations']) for r in results)
        print(f"Total violation events: {violations}")
        
    elif args.webcam:
        engine.process_webcam(camera_id=args.camera)


if __name__ == '__main__':
    main()

