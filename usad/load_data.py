from usad import *

normal = pd.read_csv("input/normal0.csv")  # , nrows=1000)
normal = normal.drop(["window_start", "window_end", "Normal/Attack"], axis=1)
print(normal.shape)
for i in list(normal):
    normal[i] = normal[i].apply(lambda x: str(x).replace(",", "."))
normal = normal.astype(float)

from sklearn import preprocessing

min_max_scaler = preprocessing.MinMaxScaler()

x = normal.values
x_scaled = min_max_scaler.fit_transform(x)
normal = pd.DataFrame(x_scaled)

print(normal.head(2))

attack = pd.read_csv("input/attack0.csv")  # , nrows=1000)
labels = [ float(label!= 'Normal' ) for label  in attack["Normal/Attack"].values]
attack = attack.drop(["window_start", "window_end", "Normal/Attack"], axis=1)
print(attack.shape)
for i in list(attack):
    attack[i] = attack[i].apply(lambda x: str(x).replace(",", "."))
attack = attack.astype(float)

x = attack.values
x_scaled = min_max_scaler.transform(x)
attack = pd.DataFrame(x_scaled)
print(normal.head(2))

window_size = 12
windows_normal = normal.values[np.arange(window_size)[None, :] + np.arange(normal.shape[0] - window_size)[:, None]]
print(windows_normal.shape)
windows_attack = attack.values[np.arange(window_size)[None, :] + np.arange(attack.shape[0] - window_size)[:, None]]
print(windows_attack.shape)
