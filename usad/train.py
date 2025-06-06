##Training
import torch.utils.data as data_utils
from recode.load_data import windows_normal, windows_attack
from usad import *


def train():
    BATCH_SIZE = 100
    N_EPOCHS = 100
    hidden_size = 100

    w_size = windows_normal.shape[1] * windows_normal.shape[2]
    z_size = windows_normal.shape[1] * hidden_size

    windows_normal_train = windows_normal[:int(np.floor(.8 * windows_normal.shape[0]))]
    windows_normal_val = windows_normal[
                         int(np.floor(.8 * windows_normal.shape[0])):int(np.floor(windows_normal.shape[0]))]

    train_loader = torch.utils.data.DataLoader(data_utils.TensorDataset(
        torch.from_numpy(windows_normal_train).float().view(([windows_normal_train.shape[0], w_size]))
    ), batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    val_loader = torch.utils.data.DataLoader(data_utils.TensorDataset(
        torch.from_numpy(windows_normal_val).float().view(([windows_normal_val.shape[0], w_size]))
    ), batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    test_loader = torch.utils.data.DataLoader(data_utils.TensorDataset(
        torch.from_numpy(windows_attack).float().view(([windows_attack.shape[0], w_size]))
    ), batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    model = UsadModel(w_size, z_size)
    model = to_device(model, device)

    history = training(N_EPOCHS, model, train_loader, val_loader)

    plot_history(history)

    torch.save({
        'encoder': model.encoder.state_dict(),
        'decoder1': model.decoder1.state_dict(),
        'decoder2': model.decoder2.state_dict()
    }, "model.pth")


train()
