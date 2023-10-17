import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Set the device (CPU or GPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load the BERT tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
model.to(device)

# Define your training dataset, batch size, and other training hyperparameters
train_data = ...
batch_size = 32
num_epochs = 3
learning_rate = 2e-5

# Create the data loader for the training set
train_dataloader = torch.utils.data.DataLoader(train_data, batch_size=batch_size)

# Define the optimizer and loss function
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
loss_fn = torch.nn.CrossEntropyLoss()

# Fine-tune the model
model.train()
for epoch in range(num_epochs):
    for batch in train_dataloader:
        inputs = batch['input_ids'].to(device)
        labels = batch['labels'].to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = loss_fn(outputs.logits, labels)
        loss.backward()
        optimizer.step()

# Set the model to evaluation mode
model.eval()

# Define your evaluation dataset
eval_data = ...

# Create the data loader for the evaluation set
eval_dataloader = torch.utils.data.DataLoader(eval_data, batch_size=batch_size)

# Define your accuracy calculation method
def calculate_accuracy(predictions, labels):
    correct = (predictions == labels).sum().item()
    total = len(labels)
    return correct / total

# Calculate accuracy on the evaluation set
predictions = []
true_labels = []
with torch.no_grad():
    for batch in eval_dataloader:
        inputs = batch['input_ids'].to(device)
        labels = batch['labels']

        outputs = model(inputs)
        batch_predictions = outputs.logits.argmax(dim=-1).tolist()
        predictions.extend(batch_predictions)
        true_labels.extend(labels)

predictions = torch.tensor(predictions).to(device)
true_labels = torch.tensor(true_labels).to(device)

accuracy = calculate_accuracy(predictions, true_labels)
print("Accuracy:", accuracy)