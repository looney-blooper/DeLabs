import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Hyper parameters
num_epochs = 10
batch_size = 64
learning_rate = 0.001

# Data augmentation and normalization for training
transform = transforms.Compose([transforms.ToTensor()])

# Load the data
train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

# Model definition
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, 5)
        self.conv2 = nn.Conv2d(10, 20, 5)
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        out = torch.relu(self.conv1(x))
        out = torch.max_pool2d(out, 2)
        out = torch.relu(self.conv2(out))
        out = torch.max_pool2d(out, 2)
        out = out.view(-1, 320)
        out = torch.relu(self.fc1(out))
        out = self.fc2(out)
        return out

# Initialize the model, loss function and optimizer
model = CNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=learning_rate)

# Train the model
for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        if (i+1) % 100 == 0:
            print ('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}' .format(epoch+1, num_epochs, i+1, len(train_dataset)//batch_size, loss.item()))

# Save the model
torch.save(model.state_dict(), 'mnist_cnn.pth')
