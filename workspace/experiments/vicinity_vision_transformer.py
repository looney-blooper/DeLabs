class VicinityVisionTransformer(nn.Module):
    def __init__(self, num_classes: int):
        super(VicinityVisionTransformer, self).__init__()
        self.patch_embedding = nn.Conv2d(3, 768, kernel_size=16, stride=16)
        self.positional_embedding = nn.Parameter(torch.randn(1, 196, 768))
        self.transformer = nn.TransformerEncoderLayer(d_model=768, nhead=8)
        self.classifier = nn.Linear(768, num_classes)

    def forward(self, x: Tensor) -> Tensor:
        x = self.patch_embedding(x)
        x = x.flatten(2)
        x = x.transpose(-1, -2)
        x = x + self.positional_embedding
        x = self.transformer(x)
        x = x.mean(dim=1)
        x = self.classifier(x)
        return x