import warnings
import torch
from typing import List, Tuple
import json
import time
from logging import Logger
import flwr as fl
from flwr.common import Metrics
from multiprocessing import Process, Manager
import sys
sys.path.append("client")

from client.flower_client import FlowerClient


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


def run_client(server_address, device, data_size, batch_size, time_delay, status_dict):
    fl.client.start_numpy_client(
        server_address=server_address,
        client=FlowerClient(
            device=device,
            data_size=data_size,
            batch_size=batch_size,
            status_dict=status_dict
        ),
        time_delay=time_delay
    )

def print_status(status_dict : dict):
    while(1):
        for key in status_dict.keys():
            print(key, status_dict[key])
            if status_dict[key] > 0.95:
                return


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


    manager = Manager()
    status_dict = manager.dict()

    process_list = []

    # Start Flower Server
    server_proc = Process(
        target=run_server,
        args=(
            server_address,
            fl.server.ServerConfig(num_rounds=round_num),
            strategy
        )
    )
    server_proc.start()
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
                client_option["delay"],
                status_dict
            )
        )
        process_list.append(client_proc)
        client_proc.start()

    print_prc = Process(target=print_status, args=(status_dict,))
    print_prc.start()

    for process in process_list:
        process.join()

    print(status_dict)