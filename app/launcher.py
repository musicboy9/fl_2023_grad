import warnings
import torch
from typing import List, Tuple
import json
# import argparse

import flwr as fl
from flwr.common import Metrics

import sys
sys.path.append("client_class")

from client_class.flower_client import FlowerClient


# parser = argparse.ArgumentParser()
# parser.add_argument("--round_num", dest="round_num", action="store")
# parser.add_argument("--client_num", dest="client_num", action="store")
with open("launcher_option.json", "r") as option_json:
    option = json.load(option_json)

round_num = option['round_num']
client_options = option['client_info']

# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


# Define strategy
strategy = fl.server.strategy.FedAvg(evaluate_metrics_aggregation_fn=weighted_average)

# Start Flower server
fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=round_num),
    strategy=strategy,
)

warnings.filterwarnings("ignore", category=UserWarning)
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# Start Flower client
for client_option in client_options:
    fl.client.start_numpy_client(
        # server_address="222.107.251.233:8080",
        server_address="0.0.0.0:8080",
        client=FlowerClient(DEVICE),
        batch_size=client_option["batch_size"],
        data_size=client_option["data_size"],
        time_delay=client_option["delay"]
    )