import warnings
import torch
from typing import List, Tuple
import json
import time
import logging
import flwr_custom as fl
from flwr_custom.common import Metrics, date
from multiprocessing import Process, Manager
from PyQt5 import QtWidgets
import sys
import argparse

from client.flower_client import FlowerClient
from viewer.viewer import Viewer
from common_fixture import *


def weighted_average(metrics: List[ Tuple[ int, Metrics ] ]) -> Metrics:
    # Multiply accuracy of each client by number of examples used
    accuracies = [ num_examples * m[ "accuracy" ] for num_examples, m in metrics ]
    examples = [ num_examples for num_examples, _ in metrics ]

    # Aggregate and return custom metric (weighted average)
    return {"accuracy": sum(accuracies) / sum(examples)}


def show_app(status_dict, option):
    app = QtWidgets.QApplication(sys.argv)
    screen = app.primaryScreen()
    screen_size = screen.size()
    viewer = Viewer(status_dict, option, screen_size)
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


def run_client(server_address, client_id, device, data_size, batch_size, epoch_num, time_delay, thread_num, status_dict):
    fl.client.start_numpy_client(
        server_address=server_address,
        client=FlowerClient(
            device=device,
            data_size=data_size,
            batch_size=batch_size,
            epoch_num=epoch_num,
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
                self.client_num = len(self.option[CLIENT_OPTIONS])
                self.round_num = self.option[ROUND_NUM]

        except FileNotFoundError:
            self.logger.error("Invalid option file")
            sys.exit()

    def __init_status(self):
        manager = Manager()
        self.status_dict = manager.dict()
        self.status_dict[LOG] = f"{date.now_custom()}, Launcher Initiation\n"
        self.status_dict[CLIENT_NUM] = self.client_num
        self.status_dict[ROUND_NUM] = self.round_num
        self.status_dict[TRAIN_CNT_OF_ROUND] = 0

    def __init_viewer(self):
        show_prc = Process(target=show_app, args=(self.status_dict, self.option,))
        self.process_list.append(show_prc)

    def __init_server(self):
        strategy = fl.server.strategy.FedAvg(evaluate_metrics_aggregation_fn=weighted_average)

        server_proc = Process(
            target=run_server,
            args=(
                self.server_address,
                fl.server.ServerConfig(num_rounds=self.round_num),
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
                    client_option[EPOCH_NUM],
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--Option", help="Launcher Option")

    args = parser.parse_args()
    if args.Option:
        launcher = Launcher(args.Option)
        launcher.run()


