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
    # server_address="222.107.251.233:8080",
    server_address="0.0.0.0:8080",
    client=FlowerClient(DEVICE),
    time_delay=0.0
)
