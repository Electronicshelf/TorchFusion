import torchfusion as tf
from torchvision.datasets.mnist import MNIST
from torch.utils.data import DataLoader
from torchvision.transforms import transforms
import torch.nn as nn
from torch.optim import Adam
import torch.cuda as cuda

#Define a the classifier network
net = nn.Sequential(

            tf.Flatten(),
            nn.Linear(784, 100),
            nn.ReLU(),
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Linear(100, 100),
            nn.ReLU(),
            nn.Linear(100, 10)
)


batch_size = 64

#Transformations and data augmentation
transformations = transforms.Compose([
    transforms.Resize(28),
    transforms.ToTensor(),
    transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))
])


#Load the training and test sets
train_set = MNIST(root="./data",transform=transformations,download=True)
test_set = MNIST(root="./data",train=False,transform=transformations,download=True)

train_loader = DataLoader(train_set,shuffle=True,batch_size=batch_size,num_workers=4)
test_loader = DataLoader(test_set,shuffle=False,batch_size=batch_size,num_workers=4)


#Move to GPU if available
if cuda.is_available():
    net.cuda()

#Setup the optimize and a loss function
optimizer = Adam(net.parameters(),lr=0.001)
loss_fn = nn.CrossEntropyLoss()

#Top 1 Train accuracy
train_metrics = tf.Accuracy(topK=1)

#Top 1 and Top 2 train accuracy
test_metrics_top1 = tf.Accuracy(name="Top 1 Acc ",topK=1)
test_metrics_top2 = tf.Accuracy(name="Top 2 Acc ",topK=2)

#Custom Model with callbacks
class CustomModel(tf.StandardModel):
    def __init__(self,model,use_cuda_if_available=True):
        super(CustomModel,self).__init__(model,use_cuda_if_available)


    def on_epoch_start(self,epoch):
        print("Starting epoch {}".format(epoch))

    def on_epoch_end(self,epoch,train_metrics,test_metrics,train_loss,duration):
        print("End of Epoch {} , Loss: {} , Duration: {}".format(epoch,train_loss,duration))

    def on_batch_start(self,epoch,batch_num):
        print("Starting batch {} of epoch {} ".format(epoch,batch_num))

    def on_batch_end(self,epoch,batch_num,train_metrics,train_loss):
        print("End of  batch {} of epoch {} , train loss: {} ".format(epoch, batch_num,train_loss))

    def on_training_completed(self,train_metrics,test_metrics,train_duration):
        print("Total Training duration : {}".format(train_duration))

        for metric in train_metrics:
            print("{} : {}".format(metric.name,metric.getValue()))

        if test_metrics is not None:
            for metric in test_metrics:
                print("{} : {}".format(metric.name, metric.getValue()))


#Create an instance of the CustomModel
model = CustomModel(net)

def train():
    # print a summary of the network
    print(model.summary((1,28,28)))

    """
        Train the network for 20 epochs
        If in jupyter notebook, set notebook_mode=True for live progress
        you can disable batch_log if you don't need batch_level logging

        """
    model.train(train_loader, loss_fn, optimizer, [train_metrics], test_loader,
                [test_metrics_top1, test_metrics_top2], num_epochs=20,
                model_dir="mnist_mlp_saved_models",notebook_mode=False,batch_log=False,save_logs="logs2.txt")


if __name__ == "__main__":
    # always initiate training in the main loop
    train()
