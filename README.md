# Qwen2-VL Fine-tuning Guide

This repository provides tools and scripts for fine-tuning the Qwen2.5-VL model 

## Prerequisites

- Python 3.11
- Conda package manager
- CUDA-compatible GPU
- Google Cloud SDK (for downloading training images)

## Setup Instructions

1. Clone the repository:
```bash
git clone <REPO LINK>
cd Qwen2-VL-Finetune
```

2. Create and activate the conda environment:
```bash
conda env create -f environment.yaml
conda activate train
```

3. Install additional required packages:
```bash
pip install qwen-vl-utils
pip install flash-attn --no-build-isolation
```

## Google Cloud Setup (for downloading training images)

1. Install Google Cloud SDK:
```bash
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-cli
```

2. Initialize Google Cloud:
```bash
gcloud init
```
- Select your Google account
- Choose 'elite-advice-366018' as the project

## Download Training Data

1. Navigate to the images directory:
```bash
cd scripts/Images
```

2. Download ICLR images:
```bash
gsutil -m cp -r gs://scigraph2/conference_papers/Mod_ICLR_2024_Image .
```

## Training

1. Return to the repository root:
```bash
cd ../..
```

2. Start training with LoRA:
```bash
bash scripts/finetune_lora.sh
```

### Training Configuration

The default training configuration in `finetune_lora.sh` includes:
- Model: Qwen2.5-VL-3B-Instruct
- LoRA rank: 64
- Learning rate: 1e-4
- Batch size: 1
- Training epochs: 1
- Gradient accumulation steps: 1
- Mixed precision training (bf16)
- DeepSpeed Zero-3 optimization

You can modify these parameters in `scripts/finetune_lora.sh` to suit your needs.

## Additional Scripts

The repository includes several other useful scripts:
- `finetune_lora_vision.sh`: For vision-specific fine-tuning
- `finetune.sh`: For full model fine-tuning
- `finetune_video.sh`: For video fine-tuning
- `merge_lora.sh`: For merging LoRA weights with the base model

## Environment Details

The conda environment includes:
- PyTorch 2.6.0
- Transformers 4.51.3
- DeepSpeed 0.16.7
- PEFT 0.15.2
- Other necessary dependencies for training and evaluation

## Notes

- The training script uses Weights & Biases (wandb) for logging
- Gradient checkpointing is enabled by default to save memory
- You will need to login to HuggingFace and WandB Account for logging and saving checkpoints
- Training data is stored in `scripts/cleaner.json`