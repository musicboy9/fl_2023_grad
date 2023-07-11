# FL Viewer

### Summary
FL Viewer is a visualized simulation of federated learning, especially with
various client environment.
User can select each client's options such as data size,
number of threads, network delay, etc.
PyTorch image classifier will be trained and evaluated using CIFAR-10 dataset.

You can watch a demo video [here](https://youtu.be/wUQeHTmHasQ)

Based on [Flower](https://github.com/adap/flower)

### How to Install

```shell
git clone https://github.com/musicboy9/fl_viewer.git
cd fl_viewer/scripts
sh setup.sh
```

### How to Run

```shell
sh run.sh
```

### How to change Client Option

This is an example of launcher_option.json file. You can modify clients' options here.

round_num: Number of total round(each round has training and evaluating stage). You can compare the score of trained model at each round.

client_id: Each client's id. Should be distinct.

thread_num: Number of threads used when training pytorch model.

batch_size: Size of training batch.

epoch_num: Number of epoch.

data_size: This ratio (0~1) will choose how much data will each client use. Each client will use the randomly selected portion of CIFAR-10 Dataset.

delay: Every gRPC message will have a time delay in second unit. For example, client_id = 1 will need 4 more seconds compared to client_id = 0
when a message is sent to the server and get a response.

```json
{
  "round_num": 1,
  "client_options": [
    {
      "client_id": 0,
      "thread_num": 1,
      "batch_size": 32,
      "epoch_num": 5,
      "data_size": 0.3,
      "delay": 0.0
    },
    {
      "client_id": 1,
      "thread_num": 6,
      "batch_size": 16,
      "epoch_num": 5,
      "data_size": 0.3,
      "delay": 2.0
    }
  ]
}
```



Keywords: FL, PyQt5, gRPC

2023 Undergraduate Graduation Project @ SNU

