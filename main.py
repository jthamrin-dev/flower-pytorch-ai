import os
import json
import shutil
import torch
import torch.nn.functional as F
import torch.optim as optim
import torchvision
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR

from model.ResNext import resnext50_32x4d
from helpers.helpers import *

#-----------------------------------Network Functions-----------------------------------#

def train(model, device, train_loader, validate_loader, optimizer, epoch):
   model.train()
   loss_value = 0
   for index, (inputs, labels) in enumerate(train_loader):
      # inputs = batch of samples (64) || index = batch index (1)
      inputs, labels = inputs.to(device), labels.to(device)
      optimizer.zero_grad()
      output = model(inputs)
      loss = F.cross_entropy(output, labels)
      loss_value += loss.item()
      loss.backward()
      optimizer.step()

      if index == 16:
        print('Train Epoch: {} [{}/{} ({:.0f}%)]\tAverage Loss: {:.6f}'.format(
          epoch, index*len(inputs), len(train_loader.dataset), 
          100. * index / len(train_loader), loss_value / len(train_loader)))

def evaluate(model, device, evaluate_loader, valid):
   model.eval()
   loss = 0
   accuracy = 0
   with torch.no_grad():
      for inputs, labels in evaluate_loader:
         inputs, labels = inputs.to(device), labels.to(device)
         output = model.forward(inputs)
         loss += F.cross_entropy(output, labels, reduction='sum').item()  # loss is summed before adding to loss
         pred = output.argmax(dim=1, keepdim=True)  # index of the max log-probability
         accuracy += pred.eq(labels.view_as(pred)).sum().item()

   loss /= len(evaluate_loader.dataset)

   if valid:
      word = 'Validate'
   else:
      word = 'Test'

   print('\n{} set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
         word, loss, accuracy, len(evaluate_loader.dataset),
         100. * accuracy / len(evaluate_loader.dataset)))

   return loss

#--------------------------------------Main Function--------------------------------------#

def main():
   epochs = 200
   best_valid_loss = float('inf')
   device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

   #-----------------------------------Dataset Download-----------------------------------#

   running_on_google_colab = False
   files_downloaded = True

   if running_on_google_colab:
      file_path = '/content/17Flowers.zip'
      extract_to = '/content/flower_data'
   else:
      file_path = './17Flowers.zip'
      extract_to = './flower_data'
      #shutil.unpack_archive(file_path, extract_to)
      print('extracted.')

   if not files_downloaded:
      #wget.download('https://dl.dropboxusercontent.com/s/itlaky1ssv8590j/17Flowers.zip')
      #wget.download('https://dl.dropboxusercontent.com/s/rwc40rv1r79tl18/cat_to_name.json')
      shutil.unpack_archive(file_path, extract_to)
      os.remove(file_path)
      print('Files have successfully downloaded.')
   else:
      print('Files have been downloaded.')

   #-----------------------------------Data Preparation-----------------------------------#
   
   train_transform = transforms.Compose([
                              transforms.RandomChoice([
                                 transforms.RandomHorizontalFlip(p=0.5),
                                 transforms.RandomVerticalFlip(p=0.5),
                                 transforms.RandomRotation(180),
                                 ]),
                              transforms.Resize(256),
                              transforms.CenterCrop(227),
                              transforms.ToTensor()
                     ])

   validate_test_transform = transforms.Compose([
                                       transforms.Resize(256),
                                       transforms.CenterCrop(227),
                                       transforms.ToTensor()
                              ])

   # Prepares and Loads Training, Validation and Testing Data.
   train_data = datasets.ImageFolder(extract_to+'/train', transform=train_transform)
   validate_data = datasets.ImageFolder(extract_to+'/valid', transform=validate_test_transform)
   test_data = datasets.ImageFolder(extract_to+'/test', transform=validate_test_transform)

   # Defining the Dataloaders using Datasets.
   train_loader = torch.utils.data.DataLoader(train_data, batch_size=30, shuffle=True)  # 1,088.
   validate_loader = torch.utils.data.DataLoader(validate_data, batch_size=30)         # 136.
   test_loader = torch.utils.data.DataLoader(test_data, batch_size=30)                 # 136.

   #---------------------------------Plots Training Images---------------------------------#
   '''
   N_IMAGES = 25
   images, labels = zip(*[(image, label) for image, label in 
                              [train_data[i] for i in range(N_IMAGES)]])
   labels = [test_data.classes[i] for i in labels]
   plot_images(images, labels, normalize = True)
   '''

   #---------------------------------Setting up the Network---------------------------------#
   
   model = resnext50_32x4d().to(device)
   optimizer = optim.Adam(model.parameters(), lr=0.001)
   
   print(f'Device selected: {str(device).upper()}')
   print(f'\nNumber of training samples: {len(train_data)}')
   print(f'Number of validation samples: {len(validate_data)}')
   print(f'Number of testing samples: {len(test_data)}')

   #----------------------------------Training the Network----------------------------------#
   valid_loss = 1
   for epoch in range(1, epochs+1):
      train(model, device, train_loader, validate_loader, optimizer, epoch)
      valid_loss = evaluate(model, device, validate_loader, 1)
      
      if valid_loss < best_valid_loss:
         best_valid_loss = valid_loss
         torch.save(model.state_dict(), 'ResNext-model.pt')
         print('Current Best Valid Loss: {:.4f}.\n'.format(best_valid_loss))
         

   #-----------------------------------Testing the Network-----------------------------------#

   model.load_state_dict(torch.load('ResNext-model.pt'))
   evaluate(model, device, test_loader, 0)

if __name__ == '__main__':
   main()
