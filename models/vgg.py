'''

DISCLAIMER: ALL CODE IS WRITTEN FROM SCRATCH AND MAY CONTAIN SIMILARITIES TO CODE FOUND ONLINE.
            APPROPRIATE ACKNOWLEDGEMENTS HAVE BEEN MADE WHERE NECESSARY.

The VGG-16 implementation below is identical to the published paper with minor tweaks.
All layers and parameters used have been referenced to their appropriate sections of the report.
Weight initialisation has been adapted from PyTorch.
Note: Identical layers have not been commented due to similarities with other comments.

Link: https://arxiv.org/pdf/1409.1556.pdf

'''

import torch
import torch.nn as nn

class VGG16(nn.Module):

    def __init__(self):
        super(VGG16, self).__init__()
        self.features = nn.Sequential(
            # Conv. Layer 1.
                # 2D Convolution applied based on Section 2.2 - Configurations, Table 1.
            nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, stride=1, padding=1),
                # EXTRA: Added Batch Normalisation to improve accuracy (NOT in official paper).
            nn.BatchNorm2d(num_features=64),
                # ReLU Activation Function based on Section 2.1 - Architecture.
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, 1, 1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
                # Max Pooling based on Section 2.1 - Architecture.
            nn.MaxPool2d(kernel_size=2, stride=2),

            # Conv. Layer 2.
            nn.Conv2d(64, 128, 3, 1, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, 1, 1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # Conv. Layer 3.
            nn.Conv2d(128, 256, 3, 1, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, 1, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, 1, 1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # Conv. Layer 4.
            nn.Conv2d(256, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # Conv. Layer 5.
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.Conv2d(512, 512, 3, 1, 1),
            nn.BatchNorm2d(512),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2)
        )

        # Average Pooling as per Section A.2 - Localisation Experiments.
        self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
        
        self.classifier = nn.Sequential(
            # Linear transformations based on Section 2.3 - Discussions.
            nn.Linear(512 * 7 * 7, 4096),
            # ReLU and Dropout based on Section 2.3 - Discussions.
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, 17),
        )

        # Initializes weights.
        self._initialize_weights()
    
    # Forward() links all the layers together
    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

    # This initializes the weights based on specifications from the official paper.
    # Adapted from PyTorch GitHub
    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)