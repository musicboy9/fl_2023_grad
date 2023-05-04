import torch
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
from torchvision.transforms import Compose, Normalize, ToTensor
from tqdm import tqdm

from net import Net


class CustomTorch:

    def __init__(self, device):
        self.device = device
        self.net = Net().to(self.device)

    def get_net(self):
        return self.net

    def train(self, trainloader, epochs):
        """Train the model on the training set."""
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.net.parameters(), lr=0.001, momentum=0.9)
        for _ in range(epochs):
            for images, labels in tqdm(trainloader):
                optimizer.zero_grad()
                criterion(self.net(images.to(self.device)), labels.to(self.device)).backward()
                optimizer.step()

    def test(self, testloader):
        """Validate the model on the test set."""
        criterion = torch.nn.CrossEntropyLoss()
        correct, loss = 0, 0.0
        with torch.no_grad():
            for images, labels in tqdm(testloader):
                outputs = self.net(images.to(self.device))
                labels = labels.to(self.device)
                loss += criterion(outputs, labels).item()
                correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
        accuracy = correct / len(testloader.dataset)
        return loss, accuracy

    def load_data(self):
        """Load CIFAR-10 (training and test set)."""
        trf = Compose([ToTensor(), Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        trainset = CIFAR10("./data", train=True, download=True, transform=trf)
        testset = CIFAR10("./data", train=False, download=True, transform=trf)
        return DataLoader(trainset, batch_size=32, shuffle=True), DataLoader(testset)
