import torch.utils.data as data_utils
from recode.load_data import windows_normal, windows_attack, labels, window_size
from usad import *


def model_test():
    BATCH_SIZE = 100
    N_EPOCHS = 100
    hidden_size = 100

    checkpoint = torch.load("model.pth")
    w_size = windows_normal.shape[1] * windows_normal.shape[2]
    z_size = windows_normal.shape[1] * hidden_size
    model = UsadModel(w_size, z_size)
    model = to_device(model, device)

    model.encoder.load_state_dict(checkpoint['encoder'])
    model.decoder1.load_state_dict(checkpoint['decoder1'])
    model.decoder2.load_state_dict(checkpoint['decoder2'])

    test_loader = torch.utils.data.DataLoader(data_utils.TensorDataset(
        torch.from_numpy(windows_attack).float().view(([windows_attack.shape[0], w_size]))
    ), batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    results = testing(model, test_loader)
    windows_labels = []
    for i in range(len(labels) - window_size):
        windows_labels.append(list(np.int_(labels[i:i + window_size])))

    y_test = [1.0 if (np.sum(window) > 0) else 0 for window in windows_labels]
    y_pred = np.concatenate([torch.stack(results[:-1]).flatten().detach().cpu().numpy(),
                             results[-1].flatten().detach().cpu().numpy()])
    # ===== 添加NaN检查和处理 =====
    print(f"NaN values in y_pred: {np.isnan(y_pred).sum()}")
    y_pred = np.nan_to_num(y_pred, nan=np.nanmean(y_pred))  # 用均值替换NaN

    threshold = ROC(y_test, y_pred)


model_test()
