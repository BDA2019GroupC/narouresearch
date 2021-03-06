import os
import torch
import argparse
from datetime import datetime
from narouresearch.networks.styleEncoder.train import train

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="this program is styleEncoder train")
    parser.add_argument("--aozora_path", help="source path aozora",required=True)
    parser.add_argument("--narou_path", help="source path narou",required=True)
    parser.add_argument("--hidden_size", default=512, type=int)
    parser.add_argument("--output_size", default=512, type=int)
    parser.add_argument("--max_epoch", default=500, type=int)
    parser.add_argument("--steps", type=int)
    parser.add_argument("--sub_steps", type=int, required=True)
    parser.add_argument("--validation_steps", type=int)
    parser.add_argument("--early_stopping", type=int, required=True)
    parser.add_argument("--method", required=True, choices=['RNN', 'GRU', 'Transformer'])
    parser.add_argument("--save_dir",required=True)
    parser.add_argument("--saved_model_dir")
    parser.add_argument("--device", choices=['cpu','gpu'])
    parser.add_argument("--margin", type=float)
    parser.add_argument("--examples_path")
    
    args = parser.parse_args()
    aozora_path = args.aozora_path
    narou_path = args.narou_path
    save_dir = args.save_dir
    max_epoch = args.max_epoch
    steps = args.steps
    sub_steps = args.sub_steps
    validation_steps = args.validation_steps
    early_stopping = args.early_stopping
    method = args.method
    saved_model_dir = args.saved_model_dir
    device = args.device
    margin = args.margin
    examples_path = args.examples_path

    if device == "gpu":
        if torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            print("cuda is not available.")
            exit()
    else: device = torch.device("cpu")
    print(device)

    save_dir = save_dir + method
    save_dir = os.path.join(save_dir,datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(save_dir, exist_ok=True)
    
    paths = (aozora_path, narou_path)

    examples = []
    if examples_path is not None:
        with open(examples_path) as f:
            for line in f:
                examples.append(line.rstrip())

    train(paths=paths, save_dir=save_dir, hidden_size=hidden_size, output_size=output_size, max_epoch=max_epoch, steps=steps,
        sub_steps=sub_steps, validation_steps=validation_steps, early_stopping=early_stopping, 
        method=method, device=device, saved_model_dir=saved_model_dir, margin=margin, examples=examples)