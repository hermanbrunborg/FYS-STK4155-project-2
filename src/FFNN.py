from tqdm import tqdm
import numpy as np
from layers import LinearLayer, SigmoidLayer


class FFNN:
    def __init__(
        self,
        n_inputs,
        hidden_sizes,
        n_categories=1,
        hidden_layers=SigmoidLayer,
        final_layer=LinearLayer,
        classification=False,
        epochs=1000,
        learning_rate=0.001,
        lambda_=0,
        verbose=False,
    ):
        """Initialize the FFNN

        Parameters
        ----------
            n_inputs : int
                number of inputs
            hidden_sizes : list
                list of hidden layer sizes
            n_categories : int
                number of categories
            hidden_layers : class
                hidden layer class
            final_layer : class
                final layer class
            classification : bool
                whether the network is a classification problem
            epochs : int
                number of epochs
            learning_rate : float
                learning rate
            lambda_ : float
                regularization parameter
            verbose : bool
                whether to print progress
        """
        self.n_inputs = n_inputs
        self.n_categories = n_categories
        self.n_hidden_layers = len(hidden_sizes)
        self.classification = classification
        self.sizes = [self.n_inputs] + list(hidden_sizes) + [self.n_categories]
        self.layers = []
        self.lambda_ = lambda_
        self.epochs = epochs
        self.verbose = verbose
        self.learning_rate = learning_rate

        self.layers.append(LinearLayer(1, 1))
        for i in range(len(self.sizes) - 1):
            if i != len(self.sizes) - 1:
                self.layers.append(hidden_layers(self.sizes[i], self.sizes[i + 1]))
            else:
                self.layers.append(final_layer(n_categories, n_categories))

    def forward(self, x):
        """Forward pass through the network

        Parameters
        ----------
            x : numpy.ndarray
                input data

        Returns
        -------
            numpy.ndarray
                predicted values
        """
        self.layers[0].output = x.reshape(1, -1)
        for i in range(self.n_hidden_layers + 1):
            self.layers[i + 1].forward(self.layers[i].output)
        return self.layers[-1].output

    def backward(self, y, learning_rate):
        """Backward pass through the network

        Parameters
        ----------
            y : numpy.ndarray
                target values
            learning_rate : float
                learning rate
        """
        L = self.n_hidden_layers + 1
        delta = self.layers[L].output - y

        if self.lambda_ == 0:
            cost = self.cost(self.layers[L].output, y)
        else:
            cost = self.cost_with_regularization(
                self.layers[L].output, y, lambda_=self.lambda_
            )
        self.costs.append(cost)

        for k in range(L, 0, -1):
            delta = self.layers[k].backward(
                delta, self.layers[k - 1].output.T, learning_rate, self.lambda_
            )

    def fit(self, X, Y):
        """Fit the model to the training data

        Parameters
        ----------
            X : numpy.ndarray
                input data
            Y : numpy.ndarray
                target values
        """
        self.costs = []
        for e in (
            tqdm(range(self.epochs), total=self.epochs, unit="epochs")
            if self.verbose
            else range(self.epochs)
        ):
            for x, y in zip(X, Y):
                self.forward(x)
                self.backward(y, learning_rate=self.learning_rate)
        # group cost by each epoch
        self.costs = np.sum(
            np.array(self.costs).reshape(
                (self.epochs, int(len(self.costs) / self.epochs))
            ),
            axis=1,
        )

    def predict(self, X):
        """Predict the output of the network

        Parameters
        ----------
            X : numpy.ndarray
                input data

        Returns
        -------
            numpy.ndarray
                predicted values
        """
        Y_pred = []
        for x in X:
            y_pred = self.forward(x)
            Y_pred.append(y_pred)
        if self.classification:
            return np.array(Y_pred).squeeze() > 0.5
        return np.array(Y_pred).squeeze()

    def cost(self, y_hat, y):
        """Calculate the cost of the network

        Parameters
        ----------
            y_hat : numpy.ndarray
                predicted values
            y : numpy.ndarray
                target values

        Returns
        -------
            float
                cost
        """
        m = len(y_hat)
        if self.classification:
            cost = -1 / m * np.nansum(y * np.log(y_hat) + (1 - y) * np.log(1 - y_hat))
        else:
            cost = 1 / m * np.nansum((y - y_hat) ** 2)
        return cost

    def cost_with_regularization(self, y_hat, y, lambda_):
        """Calculate the cost of the network with regularization

        Parameters
        ----------
            y_hat : numpy.ndarray
                predicted values
            y : numpy.ndarray
                target values
            lambda_ : float
                regularization parameter

        Returns
        -------
            float
                cost
        """
        m = len(y_hat)
        cost = self.cost(y_hat, y)
        L2_regularization_cost = (
            lambda_ / (2 * m) * np.nansum(np.square(self.layers[1].weights))
        )
        reg_cost = cost + L2_regularization_cost
        return reg_cost
