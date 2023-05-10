import warnings
import torch
from typing import List, Tuple
import json
import time
from logging import Logger
import flwr as fl
from flwr.common import Metrics
from multiprocessing import Process
import sys
sys.path.append("client_class")

from client_class.flower_client import FlowerClient


# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


def run_server(server_address, config, strategy):
    fl.server.start_server(
        server_address=server_address,
        config=config,
        strategy=strategy,
    )


def run_client(server_address, device, data_size, batch_size, time_delay):
    fl.client.start_numpy_client(
        server_address=server_address,
        client=FlowerClient(
            device=device,
            data_size=data_size,
            batch_size=batch_size
        ),
        time_delay=time_delay
    )

if __name__ == "__main__":
    # logger = Logger()
    warnings.filterwarnings("ignore", category=UserWarning)
    DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    with open("launcher_option.json", "r") as option_json:
        option = json.load(option_json)

    round_num = option['round_num']
    client_options = option['client_info']
    strategy = fl.server.strategy.FedAvg(evaluate_metrics_aggregation_fn=weighted_average)
    server_address = "0.0.0.0:8080"

    # Start Flower Server
    process_list = []
    server_proc = Process(
        target=run_server,
        args=(
            server_address,
            fl.server.ServerConfig(num_rounds=round_num),
            strategy
        )
    )
    server_proc.start()
    process_list.append(server_proc)
    print("server start")
    time.sleep(5)

    for client_option in client_options:
        client_proc = Process(
            target=run_client,
            args=(
                server_address,
                DEVICE,
                client_option["data_size"],
                client_option["batch_size"],
                client_option["delay"]
            )
        )
        process_list.append(client_proc)
        client_proc.start()
        print("client start")

    for process in process_list:
        process.join()