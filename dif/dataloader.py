import torch

from torch.utils.data import DataLoader

from torchvision import datasets, transforms

import matplotlib.pyplot as plt

from scheduler import forward_diffusion_sample

from scheduler import T

import numpy as np

from PIL import Image

from torchvision import transforms 

from torch.utils.data import DataLoader

import numpy as np



data_dir = "./corals"



IMG_SIZE = 64
BATCH_SIZE = 32



# Define the transforms

transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)), 
    transforms.RandomHorizontalFlip(),  
    transforms.ToTensor(),  
    transforms.Lambda(lambda t: (t * 2) - 1)  

])



def show_tensor_image(image):
    reverse_transforms = transforms.Compose([
        transforms.Lambda(lambda t: (t + 1) / 2),
        transforms.Lambda(lambda t: t.permute(1, 2, 0)),
        transforms.Lambda(lambda t: t * 255.),
        transforms.Lambda(lambda t: t.numpy().astype(np.uint8)),
        transforms.ToPILImage(),
    ])
    
    if len(image.shape) == 4:
        image = image[0, :, :, :] 
   









dataset = datasets.ImageFolder(root=data_dir, transform=transform)
data_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
image = next(iter(data_loader))[0]






