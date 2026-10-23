import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os

# 1. Definir transformaciones de las imágenes
data_transforms = {
    'train': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

data_dir = 'dataset'

# 2. Cargar imágenes desde las carpetas
image_datasets = {
    x: datasets.ImageFolder(os.path.join(data_dir, x), data_transforms[x])
    for x in ['train', 'val']
}

dataloaders = {
    x: DataLoader(image_datasets[x], batch_size=16, shuffle=True)
    for x in ['train', 'val']
}

num_classes = len(image_datasets['train'].classes)
print(f"Clases detectadas ({num_classes}): {image_datasets['train'].classes}")

# 3. Configurar hardware (GPU si está disponible, si no CPU)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Entrenando en: {device}")

# 4. Cargar modelo preentrenado (MobileNetV2)
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)

# Congelar capas base para entrenamiento rápido
for param in model.parameters():
    param.requires_grad = False

# Reemplazar la última capa para clasificar las 10 clases
model.classifier[1] = nn.Linear(model.last_channel, num_classes)
model = model.to(device)

# 5. Definir Función de Pérdida y Optimizador
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.classifier[1].parameters(), lr=0.001)

# 6. Bucle de Entrenamiento (5 épocas)
EPOCHS = 5

for epoch in range(EPOCHS):
    print(f"\n--- Época {epoch + 1}/{EPOCHS} ---")
    
    for phase in ['train', 'val']:
        if phase == 'train':
            model.train()
        else:
            model.eval()

        running_loss = 0.0
        running_corrects = 0

        for inputs, labels in dataloaders[phase]:
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()

            with torch.set_grad_enabled(phase == 'train'):
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                loss = criterion(outputs, labels)

                if phase == 'train':
                    loss.backward()
                    optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)

        epoch_loss = running_loss / len(image_datasets[phase])
        epoch_acc = running_corrects.double() / len(image_datasets[phase])

        print(f"{phase.upper()} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")

# 7. Guardar los pesos del modelo y las clases
RUTA_GUARDADO = 'modelo/modelo_senales.pth'
torch.save({
    'model_state_dict': model.state_dict(),
    'classes': image_datasets['train'].classes
}, RUTA_GUARDADO)

print(f"\n¡Entrenamiento completado! Modelo guardado exitosamente en '{RUTA_GUARDADO}'.")