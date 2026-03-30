"""
Pure NumPy implementation of a simple Neural Network (MLP) for MNIST.
This allows real distributed ML training over LAN without requiring PyTorch,
guaranteeing it works even on pre-release Python versions like 3.14.
"""
import numpy as np

class NumpyModel:
    def __init__(self, input_size=784, hidden_size=64, output_size=10):
        # Initialize weights with Xavier/Glorot initialization
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2. / input_size)
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2. / hidden_size)
        self.b2 = np.zeros(output_size)
        
    def forward(self, X):
        # X: (batch_size, 784)
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = np.maximum(0, self.z1) # ReLU
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        
        # Softmax
        exp_z2 = np.exp(self.z2 - np.max(self.z2, axis=1, keepdims=True))
        self.probs = exp_z2 / np.sum(exp_z2, axis=1, keepdims=True)
        return self.probs
        
    def backward(self, X, y, lr=0.01):
        m = X.shape[0]
        
        # Gradient of categorical cross entropy + softmax
        dz2 = self.probs.copy()
        dz2[range(m), y] -= 1
        dz2 /= m
        
        dW2 = np.dot(self.a1.T, dz2)
        db2 = np.sum(dz2, axis=0)
        
        da1 = np.dot(dz2, self.W2.T)
        dz1 = da1 * (self.z1 > 0) # ReLU derivative
        
        dW1 = np.dot(X.T, dz1)
        db1 = np.sum(dz1, axis=0)
        
        # Update weights
        self.W1 -= lr * dW1
        self.b1 -= lr * db1
        self.W2 -= lr * dW2
        self.b2 -= lr * db2
        
        # Calculate loss (for reporting)
        corect_logprobs = -np.log(self.probs[range(m), y] + 1e-10)
        loss = np.sum(corect_logprobs) / m
        return loss

    def get_weights(self):
        return {
            'W1': self.W1.tolist(),
            'b1': self.b1.tolist(),
            'W2': self.W2.tolist(),
            'b2': self.b2.tolist()
        }
        
    def set_weights(self, weights_dict):
        self.W1 = np.array(weights_dict['W1'])
        self.b1 = np.array(weights_dict['b1'])
        self.W2 = np.array(weights_dict['W2'])
        self.b2 = np.array(weights_dict['b2'])

def get_model() -> NumpyModel:
    return NumpyModel()
