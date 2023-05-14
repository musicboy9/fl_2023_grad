import warnings
import torch
from typing import List, Tuple
import json
import time
import logging
import flwr as fl
from flwr.common import Metrics
from multiprocessing import Process, Manager
import sys

sys.path.append("client")

from client.flower_client import FlowerClient

from viewer.progress_viewer import ProgressViewer
from PyQt5 import QtWidgets

from common_fixture import *


def weighted_average(metrics: List[ Tuple[ int, Metrics ] ]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [ num_examples * m[ "accuracy" ] for num_examples, m in metrics ]
    examples = [ num_examples for num_examples, _ in metrics ]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


def show_app(status_dict, option):
    app = QtWidgets.QApplication(sys.argv)
    viewer = ProgressViewer(status_dict, option)
    viewer.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())


def run_server(server_address, config, strategy, status_dict):
    fl.server.start_server(
        server_address=server_address,
        config=config,
        strategy=strategy,
        status_dict=status_dict,
    )
    sys.exit()


def run_client(server_address, client_id, device, data_size, batch_size, time_delay, thread_num, status_dict):
    fl.client.start_numpy_client(
        server_address=server_address,
        client=FlowerClient(
            device=device,
            data_size=data_size,
            batch_size=batch_size,
            status_dict=status_dict,
            client_id=client_id,
            thread_num=thread_num
        ),
        time_delay=time_delay,
        status_dict=status_dict,
        client_id=client_id
    )
    sys.exit()


class Launcher:

    def __init__(self, option_file):
        self.logger = logging.Logger("launcher")
        self.logger.setLevel(logging.WARNING)

        self.server_address = "0.0.0.0:8080"

        warnings.filterwarnings("ignore", category=UserWarning)

        self.process_list = []

        self.__init_option(option_file)
        self.__init_status()
        self.__init_viewer()
        self.__init_server()
        self.__init_clients()

    def __init_option(self, option_file):
        try:
            with open(option_file, "r") as option_json:
                self.option = json.load(option_json)
        except FileNotFoundError:
            self.logger.error("Invalid option file")
            pass

    def __init_status(self):
        manager = Manager()
        self.status_dict = manager.dict()
        self.status_dict[LOG] = ""
        self.status_dict[CLIENT_NUM] = len(self.option[CLIENT_OPTIONS])
        self.status_dict[ROUND_NUM] = self.option[ROUND_NUM]

    def __init_viewer(self):
        show_prc = Process(target=show_app, args=(self.status_dict, self.option,))
        self.process_list.append(show_prc)

    def __init_server(self):
        strategy = fl.server.strategy.FedAvg(evaluate_metrics_aggregation_fn=weighted_average)

        server_proc = Process(
            target=run_server,
            args=(
                self.server_address,
                fl.server.ServerConfig(num_rounds=self.status_dict[ROUND_NUM]),
                strategy,
                self.status_dict
            )
        )

        self.process_list.append(server_proc)

    def __init_clients(self):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.client_process_list = []

        for client_option in self.option[CLIENT_OPTIONS]:
            client_proc = Process(
                target=run_client,
                args=(
                    self.server_address,
                    client_option[CLIENT_ID],
                    device,
                    client_option[DATA_SIZE],
                    client_option[BATCH_SIZE],
                    client_option[DELAY],
                    client_option[THREAD_NUM],
                    self.status_dict
                )
            )
            self.client_process_list.append(client_proc)


    def run(self):
        for process in self.process_list:
            process.start()
            time.sleep(2)
        for process in self.client_process_list:
            process.start()
        for process in (self.process_list + self.client_process_list):
            process.join()


if __name__ == "__main__":
    launcher = Launcher("launcher_option.json")
    launcher.run()