import torch
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
from torchvision.transforms import Compose, Normalize, ToTensor
from flwr.common import date
from net import Net
from app.common_fixture import *


def get_log_message(round, client_id, train=True, start=True):
    result = ""
    if train:
        result += f"round {round}: client {client_id} training "
        if start:
            result += f"start\n"
        else:
            result += f"done\n"
    else:
        result += f"round {round}: client {client_id} evaluating "
        if start:
            result += f"start\n"
        else:
            result += f"done\n"
    return result


class CustomTorch:

    def __init__(self, device, data_size, batch_size, status_dict, client_id, thread_num):
        self.device = device
        self.net = Net().to(self.device)
        self.data_size = data_size
        self.batch_size = batch_size
        self.status_dict = status_dict
        self.client_id = client_id
        self.thread_num = thread_num
        self.status_dict[ROUND] = 0

    def get_net(self):
        return self.net

    def train(self, trainloader, epochs):
        """Train the model on the training set."""
        data_len = len(trainloader)

        self.status_dict[LOG] += get_log_message(round=self.status_dict[ROUND], client_id=self.client_id, train=True, start=True)

        self.status_dict[ (self.client_id, self.status_dict[ROUND], TRAIN) ] = [ date.now(), 0, data_len ]

        torch.set_num_threads(self.thread_num)
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.SGD(self.net.parameters(), lr=0.001, momentum=0.9)
        for _ in range(epochs):
            i = 0
            for images, labels in trainloader:
                i += 1
                self.status_dict[(self.client_id, self.status_dict[ROUND], TRAIN)] = [date.now(), i, data_len]

                optimizer.zero_grad()
                criterion(self.net(images.to(self.device)), labels.to(self.device)).backward()
                optimizer.step()

        self.status_dict[LOG] += get_log_message(round=self.status_dict[ROUND], client_id=self.client_id, train=True, start=False)

    def test(self, testloader):
        """Validate the model on the test set."""
        data_len = len(testloader)

        self.status_dict[LOG] += get_log_message(round=self.status_dict[ROUND], client_id=self.client_id, train=False, start=True)

        self.status_dict[ (self.client_id, self.status_dict[ROUND], EVAL) ] = [ date.now(), 0, data_len ]

        criterion = torch.nn.CrossEntropyLoss()
        correct, loss = 0, 0.0
        with torch.no_grad():
            i = 0
            for images, labels in testloader:
                i += 1
                self.status_dict[ (self.client_id, self.status_dict[ROUND], EVAL) ] = [ date.now(), i, data_len ]

                outputs = self.net(images.to(self.device))
                labels = labels.to(self.device)
                loss += criterion(outputs, labels).item()
                correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
        accuracy = correct / len(testloader.dataset)

        self.status_dict[LOG] += get_log_message(round=self.status_dict[ROUND], client_id=self.client_id, train=False, start=False)

        self.status_dict[ROUND] += 1
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

        self.status_dict[(self.client_id, "data_size")] = (self.data_size)
        return DataLoader(custom_trainset, batch_size=self.batch_size, shuffle=True), DataLoader(custom_testset)
