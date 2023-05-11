import torch
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
from torchvision.transforms import Compose, Normalize, ToTensor
import time

from flwr.common import date

from net import Net


class CustomTorch:

    def __init__(self, device, data_size, batch_size, status_dict, client_id):
        self.device = device
        self.net = Net().to(self.device)
        self.data_size = data_size
        self.batch_size = batch_size
        self.status_dict = status_dict
        self.client_id = client_id

    def get_net(self):
        return self.net

    def train(self, trainloader, epochs):
        """Train the model on the training set."""
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.net.parameters(), lr=0.001, momentum=0.9)
        for _ in range(epochs):
            self.status_dict[self.client_id] = [date.now(), 0]
            i = 0
            data_len = len(trainloader)
            for images, labels in trainloader:
                i += 1
                self.status_dict[self.client_id] = [date.now(), i/data_len]

                optimizer.zero_grad()
                criterion(self.net(images.to(self.device)), labels.to(self.device)).backward()
                optimizer.step()

    def test(self, testloader):
        """Validate the model on the test set."""
        criterion = torch.nn.CrossEntropyLoss()
        correct, loss = 0, 0.0
        with torch.no_grad():
            for images, labels in testloader:
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
        custom_data_train_len = int(len(trainset) * self.data_size)
        custom_trainset = torch.utils.data.random_split(trainset, [custom_data_train_len, len(trainset) - custom_data_train_len])[0]

        testset = CIFAR10("./data", train=False, download=True, transform=trf)
        custom_data_test_len = int(len(testset) * self.data_size)
        custom_testset = torch.utils.data.random_split(testset, [custom_data_test_len, len(testset) - custom_data_test_len])[0]

        return DataLoader(custom_trainset, batch_size=self.batch_size, shuffle=True), DataLoader(custom_testset)
