import torch
import torch.optim as optim
import torch.nn as nn
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
import numpy as np
import os, sys, time, pickle

numEpochs = 2
classesOfInterest = ('airplane', 'automobile', 'deer', 'dog')

#########################################################################
#				LOAD DATA			        #
#########################################################################

transform = transforms.Compose([transforms.Grayscale(num_output_channels=1), transforms.ToTensor()])

print("\nLoading CIFAR-10 Training Set")
print("\t", end="")
trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
trainloader = torch.utils.data.DataLoader(trainset, batch_size=4, shuffle=True, num_workers=2)
print("\tSize of Training Set: " + str(trainset.__len__()))
print("\nLoading CIFAR-10 Testing Set")
print("\t", end="")
testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)
testloader = torch.utils.data.DataLoader(testset, batch_size=4, shuffle=False, num_workers=2)
print("\tSize of Testing Set: " + str(testset.__len__()))
filename="./data/cifar-10-batches-py/batches.meta"
with open(filename, mode='rb') as file:
        # In Python 3.X it is important to set the encoding,
        # otherwise an exception is raised here.
        data = pickle.load(file, encoding='bytes')[b'label_names']
names = [x.decode('utf-8') for x in data]
coiIndices = []
for c in classesOfInterest:
	if(c in names):
		coiIndices.append(names.index(c))
#########################################################################
#			INITIALIZE NEURAL NETWORK		        #
#########################################################################

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

print("\nCreating Network")
net = Net()
print("\twith Loss and Optimizer")
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

#########################################################################
#			   TRAIN NETWORK				#
#########################################################################

tbWidth = 50
tbUpFreq = (trainloader.__len__() * numEpochs) / tbWidth
print("\tTraining on", numEpochs, "Epochs")
sys.stdout.write("\t[%s]" % (" " * tbWidth))
sys.stdout.flush()
sys.stdout.write("\b" * (tbWidth+1)) # return to start of line, after '['
for epoch in range(numEpochs):  # loop over the dataset multiple times
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):

        # get the inputs
        inputs, labels = data

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # update loading bar
        running_loss += loss.item()
        if i % (tbUpFreq) == 1:
            sys.stdout.write("#")
            sys.stdout.flush()
            #print('[%d, %5d] loss: %.3f' %(epoch + 1, i + 1, running_loss / 2000))
            running_loss = 0.0
print('] 100%')

#########################################################################
#				TEST NETWORK				#
#########################################################################

dataiter = iter(testloader)
images, labels = dataiter.next()

outputs = net(images)

_, predicted = torch.max(outputs, 1)

print('Predicted: ', ' '.join('%5s' % classes[predicted[j]] for j in range(4)))

correct = 0
total = 0
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print('Accuracy of the network on the 10000 test images: %d %%' % (100 * correct / total))

class_correct = list(0. for i in range(10))
class_total = list(0. for i in range(10))
with torch.no_grad():
    for data in testloader:
        images, labels = data
        outputs = net(images)
        _, predicted = torch.max(outputs, 1)
        c = (predicted == labels).squeeze()
        for i in range(4):
            label = labels[i]
            class_correct[label] += c[i].item()
            class_total[label] += 1
i = 0
for classType in classesOfInterest:
    ind = coiIndices(i)
    print('Accuracy of %5s : %2d %%' % (classType, 100 * class_correct[ind] / class_total[ind]))
    i = i + 1
