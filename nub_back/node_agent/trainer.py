import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
from metrics_sender import send_metrics

class SimpleCNN(nn.Module):
    """A minimal CNN for fast training on MNIST."""
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, 3, 1)
        self.conv2 = nn.Conv2d(16, 32, 3, 1)
        self.fc1 = nn.Linear(32 * 5 * 5, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = torch.flatten(x, 1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return torch.log_softmax(x, dim=1)

def train_mnist_job(job_id: str, epochs: int, node_id: str):
    """Executes the MNIST training job."""
    print(f"[*] Starting training job {job_id} for {epochs} epochs")
    
    # Use CPU to keep demo simple and guaranteed to run on any laptop without driver configs
    device = torch.device("cpu")
    model = SimpleCNN().to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Setup dataset, using a very small subset so epochs complete in seconds during demo
    transform = transforms.Compose([
        transforms.ToTensor(), 
        transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # download=True will fetch the dataset if not present
    full_dataset = datasets.MNIST('../data', train=True, download=True, transform=transform)
    
    # Subset of 1000 items (fast epochs)
    subset_indices = list(range(1000))
    train_dataset = Subset(full_dataset, subset_indices)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    
    from tqdm import tqdm
    
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        # Use tqdm for animated progress bar
        pbar = tqdm(enumerate(train_loader), total=len(train_loader), desc=f"Epoch {epoch}/{epochs}", leave=True, bar_format="{l_bar}{bar:30}{r_bar}")
        
        for batch_idx, (data, target) in pbar:
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = nn.functional.nll_loss(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)
            
            # Update progress bar
            pbar.set_postfix({'loss': f"{loss.item():.4f}", 'acc': f"{100.*correct/total:.2f}%"})
            
        avg_loss = total_loss / len(train_loader)
        accuracy = 100. * correct / total
        
        print(f"[*] ✅ Epoch {epoch} Complete - Final Acc: {accuracy:.2f}% | Final Loss: {avg_loss:.4f}\n")
        
        # Stream metrics back to central server
        send_metrics(job_id, epoch, round(accuracy, 2), round(avg_loss, 4), node_id)
        
    print(f"[*] 🎉 Job {job_id} completed successfully")
