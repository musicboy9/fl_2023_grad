import warnings
import flwr as fl
import torch

import sys
sys.path.append("client_class")

from client_class.flower_client import FlowerClient

warnings.filterwarnings("ignore", category=UserWarning)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Start Flower client
fl.client.start_numpy_client(
    server_address="127.0.0.1:8080",
    client=FlowerClient(DEVICE),
)
