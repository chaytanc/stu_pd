# vim: set sw=4 noet ts=4 fileencoding=utf-8:

#import sys
#sys.path.append(../my_scraper/code)
#import main_new
import torch
import torch.nn as nn
import torch.nn.functional as f
import torch.optim as optim
from torch.utils.data import Dataset, Dataloader
from torchvision import datasets, transforms
import pandas as pd

# Separate data sets:
    # Training
    # Validation
        # Need to get by having legit angellist account and tracking outcome of
        # predictions
        # Or make validation set with already successful/determined fates of
        # companies
    # Actual/Test

# Get training data
# This class redefines Dataset functions so that we can use dataloader
class Company_Name_Dataset(Dataset):
	def __init__(self):
		#XXX get pd dataset and select 'title' of company only
		#XXX pass in output location to read
		df = pd.read_csv('../output/out.csv')
		col = df['title'].values
		
		# This took values from title column and turned to a torch tensor
		titles = torch.from_numpy(col)
		# Same thing but for the raised values
		# Raised will be used as the labels for the network
		raised = torch.from_numpy(df['raised'].values)

		#XXX titles and raised are now of the type Tensor, but I'm not sure they
		# will backpropagate
		titles.requires_grad = True
		raised.requires_grad = True

	# Overriding __len__ and __getitem__ is necessary for custom Dataset
	# Length of your dataset
	def __len__(self, titles):
		data_len = len(titles)
		return data_len 

	# Which items you will use from your dataset
	def __getitem__(self, idx):
		sample = self.titles[idx]
		return sample

	#XXX
	def preprocess_titles(self, titles):
		''' Converts titles, a list of strings, into a list of arrays.
		>>> titles = ['Quen']
		>>> titles = s.preprocess_titles(titles)
		>>> titles[0] == [81, 117, 101, 110]
		True
		'''
		# Empty list which will fill with lists of each title in integer form
		int_titles = []
		for title in titles:
			# Make an empty list for each company name in titles
			int_title = []
			for char in title:
				int_title.append(ord(char))
		return int_titles

# example of how to use this dataset, prob not the actual implementation
# of accessing this dataset
if __name__ == '__main__':
	dataset = Company_Name_Dataset
	training_data = DataLoader(dataset=dataset, batch_size=20, 

    # csv with columns of company name, raised, joined, stage, desc, etc...
    # separate/parse?

# Define network
class Net(nn.Module):
    # Layers
	#XXX make settings file for easily tweaking training values
	#XXX make layers func based on # of layers desired passed in
    def __init__(self, input_layer_size, hidden_size, layer_output_size):
        super(Net, self).__init__()
        self.layer1 = nn.Linear(input_layer_size, layer_output_size)
		self.layer2 = nn.Linear(input_layer_size, layer_output_size)
		#XXX
		# make an array constituing the hidden layer(s)

	# change to just pass in input_layer which should
    def forward(self, joined_date, location, market, product_desc, raised, 
		signal, size, stage, title, website):

		# Passing stuff through the net
		# To pass each input node to each hidden layer node
		# for attrib in input_layer
			# for node in hidden_layer
			# f.relu(node(attrib))
		# f is functional module from torch
        joined = f.relu(self.layer1(joined))
		joined = f.relu(self.layer2(joined))
		signal = f.relu(self.layer1(signal))
		signal = f.relu(self.layer2(signal))
		output = torch.cat(joined, signal)

        return output 

# Load data
# Train:
    # Evaluation with training/validation set
net = Net()
#XXX need to pass in
sgd_optimizer = optim.SGD(net.parameters(), lr=learning_rate, momentum=momentum)
# often call 'criterion'
loss_function = nn.NLLLoss()
    # Prediction/output
	def train_net(epochs, training_data):
		# This defines how many times you want to go over the dataset for train
	    for epoch in range(epochs):
			# This iterates over batches. Batches makes it so you don't have
			# to calc the gradient as frequently
	        for batch_idx, (data, target) in enumerate(training_data):
				#XXX supervised?
				data, target = Variable(data), Variable(target)
				# ex params: -1, 28*28
				data = data.view(data_size_flattened)
				optimizer.zero_grad()
				#XXX ??
				net_out = net(datas...)
				loss = loss_function(net_out, target)
				loss.backward()
				optimizer.step()
				# If the # of times we have iterated through the same data is
				# divisible by the freq. we want to display log then print
				if batch_idx % log_interval == 0:
					print('Train Epoch: {}, Loss: {}'.format(
						epoch, loss.data[0]))




# Predict with actual data/run code
    # Maybe make better by getting better data such as company finances
	def test_net():
		test_loss = 0
		correct = 0
		for data, target in test_loader:
			#XXX volitile?
			data, target = Variable(data, volatile=True), Variable(target)
			#XXX do for all input nodes
			data.view(size)
			net_out = net(data...)
			test_lost += loss_function(net_out, target)
			#XXX?
			pred = net_out.data.max(1)[1]
			correct += pred.eq(target.data)

			test_loss /= len(test_loader.dataset)
			print('\nTest set: ' +\
			'Avg. loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
				test_loss, correct, len(test_loader.dataset), 
				100. * correct / len(test_loader.dataset)))

# Track result of actual data:
    # Turn actual into validation and continually
    # strengthen algorithm



