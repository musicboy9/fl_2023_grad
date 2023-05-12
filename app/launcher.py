import warnings
from collections import defaultdict
import torch
from typing import List, Tuple
import json
import time
from logging import Logger
import flwr as fl
from flwr.common import Metrics, date
from multiprocessing import Process, Manager
import sys
sys.path.append("client")

from client.flower_client import FlowerClient

from viewer.progress_viewer import MyWidget
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter


# Define metric aggregation function
def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


def run_server(server_address, config, strategy, status_dict):
    fl.server.start_server(
        server_address=server_address,
        config=config,
        strategy=strategy,
        status_dict=status_dict,
    )


def run_client(server_address, device, data_size, batch_size, time_delay, status_dict, client_id):
    fl.client.start_numpy_client(
        server_address=server_address,
        client=FlowerClient(
            device=device,
            data_size=data_size,
            batch_size=batch_size,
            status_dict=status_dict,
            client_id=client_id
        ),
        time_delay=time_delay,
        status_dict=status_dict,
        client_id=client_id
    )

# def print_status(status_dict : dict):
#     last_status = defaultdict(int)
#     while(1):
#         for id in status_dict.keys():
#             if status_dict[id] != last_status[id]:
#                 print(id, status_dict[id])
#                 last_status[id] = status_dict[id]

def show_app(status_dict):
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget(status_dict)
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())


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

    show_prc = Process(target=show_app, args=(status_dict,))
    show_prc.start()

    process_list = []

    # Start Flower Server
    server_proc = Process(
        target=run_server,
        args=(
            server_address,
            fl.server.ServerConfig(num_rounds=round_num),
            strategy,
            status_dict
        )
    )
    server_proc.start()
    time.sleep(5)

    for client_id in range(len(client_options)):
        client_option = client_options[client_id]
        client_proc = Process(
            target=run_client,
            args=(
                server_address,
                DEVICE,
                client_option["data_size"],
                client_option["batch_size"],
                client_option["delay"],
                status_dict,
                client_id
            )
        )
        process_list.append(client_proc)
        client_proc.start()

    # client_ids = range(len(client_options))
    # print_prc = Process(target=print_status, args=(status_dict,))
    # print_prc.start()
    # print_prc.join()

    for process in process_list:
        process.join()

