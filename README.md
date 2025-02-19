# Redis Analyzer

Redis Analyzer is an experimental tool designed to analyze and visualize Redis data structures and summarize the total usage of such key pattern.

## Features

- Analyze Redis data structures
- Visualize key distribution and memory usage
- Generate nice-to-view reports

## Installation

To install Redis Analyzer, clone the repository and install the dependencies:

```bash
git clone https://github.com/Tessaract-io/redis-analyzer.git
cd redis-analyzer
pip install -r requirements.txt
```

## Preparation
Connect to target namepsace of the kubernetes cluster, then port-forward the Redis service to your local device:
```bash
kubectl port-forward --address 0.0.0.0 service/redis 6380:6379
```

## Usage
To start the Redis Analyzer, use another terminal to run the following command:

```bash
# For database 0, forwarded service is at 127.0.0.1 port 6380
pthon analyze.py --host 127.0.0.1 --port 6380 --db 0 --password ""

# For database 1
pthon analyze.py --host 127.0.0.1 --port 6380 --db 1 --password ""
```

## Contributing

We welcome contributions! Please fork the repository and submit pull requests.

## License

This project is [Unlicense](LICENSE).

## Contact

For any questions or feedback, please open an issue on GitHub.
