# train.py

import os
import yaml
from ultralytics import YOLO
import matplotlib.pyplot as plt
import pandas as pd # Để đọc file kết quả dễ dàng hơn

def train_yolov8(config_path):
    """
    Huấn luyện mô hình YOLOv8 và trả về đường dẫn đến thư mục chứa kết quả.
    """
    print(f"Đang tải cấu hình từ: {config_path}")
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)

    # Khởi tạo mô hình YOLO
    # Nếu cfg['model'] là None, sẽ dùng khởi tạo ngẫu nhiên
    model = YOLO(cfg['model']) 

    print("\n--- Bắt đầu huấn luyện YOLOv8 ---")
    results = model.train(
        data=cfg['data'],
        epochs=cfg['epochs'],
        batch=cfg['batch_size'],
        imgsz=cfg['imgsz'],
        workers=cfg['workers'],
        patience=cfg['patience'],
        optimizer=cfg['optimizer'],
        lr0=cfg['lr0'],
        lrf=cfg['lrf'],
        momentum=cfg['momentum'],
        weight_decay=cfg['weight_decay'],
        warmup_epochs=cfg['warmup_epochs'],
        warmup_momentum=cfg['warmup_momentum'],
        warmup_bias_lr=cfg['warmup_bias_lr'],
        box=cfg['box'],
        cls=cfg['cls'],
        dfl=cfg['dfl'],
        hsv_h=cfg['hsv_h'],
        hsv_s=cfg['hsv_s'],
        hsv_v=cfg['hsv_v'],
        degrees=cfg['degrees'],
        translate=cfg['translate'],
        scale=cfg['scale'],
        shear=cfg['shear'],
        perspective=cfg['perspective'],
        flipud=cfg['flipud'],
        fliplr=cfg['fliplr'],
        mosaic=cfg['mosaic'],
        mixup=cfg['mixup'],
        copy_paste=cfg['copy_paste'],
        project=cfg['project'],
        name=cfg['name'],
        exist_ok=cfg['exist_ok'],
        save_period=cfg.get('save_period', -1)
    )
    print("--- Huấn luyện hoàn tất ---")
    
    # ultralytics sẽ trả về một đối tượng chứa đường dẫn thư mục lưu kết quả
    # Cần tìm đường dẫn thực tế của thư mục chạy
    # Ví dụ: runs/train/yolov8_combined
    # Cách tốt nhất là lấy từ thuộc tính `save_dir` của đối tượng trainer
    runs_dir = model.trainer.save_dir
    print(f"Kết quả được lưu tại: {runs_dir}")
    return runs_dir

def plot_map_curve(runs_dir):
    """
    Đọc file results.csv và vẽ biểu đồ mAP@0.5:0.95 theo epoch.
    """
    results_path = os.path.join(runs_dir, 'results.csv')
    
    if not os.path.exists(results_path):
        print(f"Lỗi: Không tìm thấy file results.csv tại {results_path}")
        return

    print(f"\nĐang đọc kết quả từ: {results_path}")
    # Đọc file CSV, bỏ qua dòng đầu tiên (header chứa '#' comment)
    df = pd.read_csv(results_path, comment='#')
    
    # ultralytics lưu mAP@0.5:0.95 dưới cột 'metrics/mAP50-95(B)'
    # và epochs là cột 'epoch'
    epochs = df['epoch']
    map_50_95 = df['metrics/mAP50-95(B)'] # hoặc 'metrics/mAP50-95(M)' tùy phiên bản ultralytics và task (B: box, M: mask)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, map_50_95, marker='o', linestyle='-', color='skyblue')
    plt.title('mAP@0.5:0.95 (Box) over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('mAP@0.5:0.95')
    plt.grid(True)
    plt.xticks(epochs[::len(epochs)//10].astype(int) if len(epochs) > 10 else epochs.astype(int)) # Chỉ hiện 10 tick nếu nhiều quá
    plt.tight_layout()
    
    # Lưu biểu đồ
    plot_save_path = os.path.join(runs_dir, 'mAP_50-95_curve.png')
    plt.savefig(plot_save_path)
    print(f"Biểu đồ mAP đã được lưu tại: {plot_save_path}")
    plt.show()

if __name__ == "__main__":
    # Đảm bảo file config.yaml nằm cùng thư mục với train.py
    config_file = 'config.yaml' 
    
    # 1. Thực hiện huấn luyện
    final_runs_directory = train_yolov8(config_file)
    
    # 2. Vẽ biểu đồ mAP sau khi huấn luyện
    if final_runs_directory:
        plot_map_curve(final_runs_directory)