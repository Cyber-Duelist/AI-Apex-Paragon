class Dataset:
    def __init__(self,name,num_samples):
        self.name = name
        self.num_samples = num_samples
    def summary(self):
        print(f"Dataset: {self.name} | samples: {self.num_samples} ")    
dataset1 = Dataset("MNIST",60000)
dataset2 = Dataset("HAVOC",14000)
dataset1.summary()
dataset2.summary()