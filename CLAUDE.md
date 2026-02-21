# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A machine learning project for detecting and counting **varroa mites** (*Varroa destructor*) in beehive inspection images using YOLOv11 object detection. The goal is to automatically estimate infestation levels from photos of bottom boards (planches) taken after treatment.

## Architecture

This is a **Google Colab-based ML research project**. The primary workflow lives in a single Jupyter notebook:

- [train_varroa.ipynb](train_varroa.ipynb) — Main notebook: dataset download, model evaluation, fine-tuning, inference, and result commits to GitHub
- [utils/auto_commit.py](utils/auto_commit.py) — Helper for committing training results to Git from Colab
- [model_mdpi_3291496/weights/best.pt](model_mdpi_3291496/weights/best.pt) — Pre-trained YOLO model from the MDPI research paper (Yániz et al., 2025)
- [runs/detect/](runs/detect/) — YOLO output directory: training metrics, validation results, predicted images

## ML Stack

- **Framework:** Ultralytics YOLOv11 (`ultralytics` package)
- **Dataset platform:** Roboflow (`varroa-counter` workspace, project `varroa-counter-large`)
- **Training environment:** Google Colab Pro (requires ~80GB GPU for large image sizes)
- **Dataset format:** YOLOv11 (bounding boxes, normalized coordinates)
- **Classes:** `varroa` (primary), `goutte` (water droplets — added in v5 to reduce false positives)

## Key Parameters

- **Image size for inference:** 5856px (original research) or 3900px (fine-tuning, due to GPU constraints)
  - `imgsz` must be a multiple of 32; 3900 → auto-rounded to 3904
- **Model:** YOLOv11n (nano, ~3M parameters) fine-tuned from the MDPI pre-trained weights
- **Dataset versions used:** v4 (varroa only), v5 (varroa + goutte classes)
- **max_det:** 2000 (high because images can contain hundreds of mites)
- **conf threshold:** 0.1 (low, to maximize recall)

## Running the Notebook

The notebook is designed to run in **Google Colab**, not locally. Requires:
- Colab secret `GITHUB_TOKEN` — for cloning/pushing to GitHub
- Colab secret `ROBOFLOW_API_KEY` — for downloading the dataset

Notebook cell execution order:
1. Install dependencies (`ultralytics`, `roboflow`)
2. Clone GitHub repo and configure Git
3. Download dataset from Roboflow
4. Evaluate pre-trained MDPI model
5. Fine-tune with new dataset version
6. Evaluate fine-tuned model
7. Run manual inference on specific images
8. Commit results to GitHub

## Known Issues & Context

- The MDPI pre-trained model was trained on dry boards; it poorly handles water droplets (`goutte` class) and wax debris, causing many false positives
- Small object detection in large images is the core challenge — the model struggles at val/test time (mAP50 ~2-4%) despite reasonable train performance (~55%)
- Future direction: use **SAHI** (Slicing Aided Hyper Inference) to detect small objects by slicing large images into smaller tiles before inference

## Dataset Structure (after Roboflow download)

```
varroa-counter-large-5/
  train/images/   train/labels/
  valid/images/   valid/labels/
  test/images/    test/labels/
  data.yaml
```

## Evaluation Function

The `evaluate_model_performance(setToEvaluate, modelPath, dataPath, imgsz)` function in the notebook wraps `model.val()` and prints Precision, Recall, mAP50, mAP50-95 for a given split.
