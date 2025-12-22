from torch.optim import Adam
from model import model
from dataloader import data_loader
from dataloader import BATCH_SIZE
from sampler import sample
from scheduler import T
from scheduler import forward_diffusion_sample
import torch.nn.functional as F
import torch



#loss function
def get_loss(model, x_0, t):
    x_noisy, noise = forward_diffusion_sample(x_0, t, device)
    noise_pred = model(x_noisy, t)
    return F.l1_loss(noise, noise_pred)



device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
optimizer = Adam(model.parameters(), lr=0.001)
epochs = 100 



for epoch in range(epochs):
    for step, batch in enumerate(data_loader):
      optimizer.zero_grad()
      t = torch.randint(0, T, (BATCH_SIZE,), device=device).long()
      loss = get_loss(model, batch[0], t)
      loss.backward()
      optimizer.step()
      if epoch % 2 == 0 and step == 0 and epoch !=0:
        print(f"Epoch {epoch} | step {step:03d} Loss: {loss.item()} ")
        #sample(model)
      elif step == 0:
        print(f"Epoch {epoch} | step {step:03d} Loss: {loss.item()} ")
torch.save(model.state_dict(), 'model.pth')
