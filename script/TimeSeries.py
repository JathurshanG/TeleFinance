from sklearn import random

import pandas as pd 
import numpy as np

class pepareData():
    def __init__(self):
        self.history = pd.read_csv("data/raw/History.csv")
        
    def prepareDate(self,ticket):
        history = self.history
        history = history[history['ticket']==ticket]
        history = history.reset_index(drop=True)[["Date",'Close','ticket','Volume']]
        history["time_idx"] = np.arange(len(history))               # index temporel croissant
        return history


if __name__ =="__main__":
    pp = pepareData()
    db = pp.prepareDate('SNY')

from pytorch_forecasting import TimeSeriesDataSet

# Paramètres de séquence
max_encoder_length = 60   # 60 jours d'historique
max_prediction_length = 30  # prédire 30 jours
# Dataset TFT
dataset = TimeSeriesDataSet(
    db,
    time_idx="time_idx",
    target="Close",
    group_ids=["ticket"],
    max_encoder_length=max_encoder_length,
    max_prediction_length=max_prediction_length,
    time_varying_known_reals=["time_idx"],
    time_varying_unknown_reals=["Close", "Volume"]
)


from pytorch_forecasting import TemporalFusionTransformer
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import EarlyStopping, LearningRateMonitor
import torch


# DataLoader
train_dataloader = dataset.to_dataloader(train=True, batch_size=64, num_workers=0)

# Modèle TFT
tft = TemporalFusionTransformer.from_dataset(
    dataset,
    learning_rate=0.03,
    hidden_size=16,
    attention_head_size=1,
    dropout=0.1,
    loss=torch.nn.MSELoss(),
    log_interval=10,
)

# Entraîneur
trainer = Trainer(
    max_epochs=10,
    accelerator="auto",
    callbacks=[
        EarlyStopping(monitor="train_loss", patience=3),
        LearningRateMonitor()
    ]
)

trainer.fit(tft, train_dataloaders=train_dataloader)



