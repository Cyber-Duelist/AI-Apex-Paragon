class NeuralNetwork:
    def __init__(self,input_size,output_size):
        self.input_size = input_size
        self.output_size = output_size
    def describe(self):
        print(f"This network has {self.input_size} inputs and {self.output_size} outputs")
network = NeuralNetwork(3,1)
network.describe()