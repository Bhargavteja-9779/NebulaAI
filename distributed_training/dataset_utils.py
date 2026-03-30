"""
Dataset utils using standard libraries for pure-python/NumPy ML.
Downloads MNIST idx format directly and implements mini-batching.
"""
import os
import gzip
import urllib.request
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def download_file(url, filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filepath)
    return filepath

def load_mnist_images(filename):
    with gzip.open(filename, 'rb') as f:
        data = np.frombuffer(f.read(), np.uint8, offset=16)
    data = data.reshape(-1, 784).astype(np.float32) / 255.0  # Normalize to 0-1
    return data

def load_mnist_labels(filename):
    with gzip.open(filename, 'rb') as f:
        data = np.frombuffer(f.read(), np.uint8, offset=8)
    return data

def get_mnist_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    base_url = "https://storage.googleapis.com/cvdf-datasets/mnist"
    x_train_file = download_file(f"{base_url}/train-images-idx3-ubyte.gz", "train-images-idx3-ubyte.gz")
    y_train_file = download_file(f"{base_url}/train-labels-idx1-ubyte.gz", "train-labels-idx1-ubyte.gz")
    x_test_file  = download_file(f"{base_url}/t10k-images-idx3-ubyte.gz", "t10k-images-idx3-ubyte.gz")
    y_test_file  = download_file(f"{base_url}/t10k-labels-idx1-ubyte.gz", "t10k-labels-idx1-ubyte.gz")
    
    x_train = load_mnist_images(x_train_file)
    y_train = load_mnist_labels(y_train_file)
    x_test  = load_mnist_images(x_test_file)
    y_test  = load_mnist_labels(y_test_file)
    return x_train, y_train, x_test, y_test

def get_worker_shard(worker_id: int, total_workers: int, batch_size: int = 64):
    x_train, y_train, _, _ = get_mnist_data()
    n = len(x_train)
    shard_size = n // total_workers
    start = worker_id * shard_size
    end   = start + shard_size if worker_id < total_workers - 1 else n
    
    x_shard = x_train[start:end]
    y_shard = y_train[start:end]
    
    def data_generator():
        indices = np.arange(len(x_shard))
        np.random.shuffle(indices)
        for i in range(0, len(x_shard), batch_size):
            batch_idx = indices[i:i+batch_size]
            yield x_shard[batch_idx], y_shard[batch_idx]
            
    return data_generator, len(x_shard)
