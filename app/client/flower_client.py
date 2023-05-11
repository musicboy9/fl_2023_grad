import flwr as fl
import torch
from collections import OrderedDict
from custom_torch import CustomTorch
import torch.utils.data as data_utils


# Define Flower client
class FlowerClient(fl.client.NumPyClient):

    def __init__(self, device, data_size = 1.0, batch_size = 0.0, status_dict = {}, client_id = -1):
        self.custom_torch = CustomTorch(device, data_size, batch_size, status_dict, client_id)
        self.net = self.custom_torch.get_net()
        self.status_dict = status_dict
        self.client_id = client_id

    def get_parameters(self, config):
        return [val.cpu().numpy() for _, val in self.net.state_dict().items()]

    def get_testloader(self):
        _, testloader = self.custom_torch.load_data()
        return testloader

    def get_trainloader(self):
        trainloader, _ = self.custom_torch.load_data()
        return trainloader

    def set_parameters(self, parameters):
        params_dict = zip(self.net.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.net.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        self.status_dict[self.client_id] = "fitting start"
        trainloader = self.get_trainloader()
        self.set_parameters(parameters)
        self.custom_torch.train(trainloader, epochs=1)
        self.status_dict[self.client_id] = "fitting done"
        return self.get_parameters(config={}), len(trainloader.dataset), {}

    def evaluate(self, parameters, config):
        self.status_dict[self.client_id] = "eval start"
        testloader = self.get_testloader()
        self.set_parameters(parameters)
        loss, accuracy = self.custom_torch.test(testloader)
        self.status_dict[self.client_id] = "eval done"
        return loss, len(testloader.dataset), {"accuracy": accuracy}
