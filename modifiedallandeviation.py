import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import easygui

# Define the calculate_xk function first
def calculate_xk(y, m):
    xk1 = [(sum(y[i:i+m]) / m) for i in range(len(y)-(m-1))]
    xk = [round(val, 3) for val in xk1]
    return xk

# Get the path to the text file
path = easygui.fileopenbox()
with open(path, "r") as f:
    print("Sample data\n")
    for i, line in enumerate(f):
        print(line.split(" "))
        if i > 10:
            break
    col = int(input("Select Column : "))
f.close()

data = []  # Define data as an empty list

with open(path, "r") as f:
    for line in f:
        if len(line.split(" ")) < 5:
            value = float(line.split(" ")[col-1])
        else:
            value = float(line.split(" ")[col])
        
        # Multiply the value by 10^9
        value *= 10**9
        data.append(value)
print("\ntotal points = ", len(data))

tau0 = int(input("Enter the tau0 value: "))  # User input for tau0
m_values = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 3600, 5000, 10000]  # List of m values
taus = [m * tau0 for m in m_values if m < len(data)//4]  # Calculate taus based on m values
results = []
zero_mdev_count = 0  # Counter for consecutive zero MDEV values

for tau in taus:
    m = tau // tau0  # Allan deviation window size parameter
    N = len(data)
    xk = calculate_xk(data, m)

    def calculate_y_prime(xk, tau, m):
        y_prime1 = [(xk[i+m] - xk[i]) / tau for i in range(len(xk) - m)]
        y_prime = [round(val, 3) for val in y_prime1]
        return y_prime

    # Calculate xk and y_prime
    xk = calculate_xk(data, m)
    y_prime = calculate_y_prime(xk, tau, m)

    # Calculate y'(k+m) - y'(k)
    y_diff1 = [y_prime[k + m] - y_prime[k] for k in range(len(y_prime) - m)]
    y_diff = [round(val, 3) for val in y_diff1]

    # Calculate the sum of squares
    sum_squares = sum(x**2 for x in y_diff)

    MDEV = np.sqrt(sum_squares / (2*(N - 3*m + 1)))

    # Multiply the MAD by 10^-9
    MDEV *= 10**(-9)

    if MDEV == 0:
        zero_mdev_count += 1
        if zero_mdev_count >= 2:
            print(f"Stopping calculation as MDEV is 0 for 2 consecutive values.")
            break
    else:
        zero_mdev_count = 0

    # Calculate TDEV
    TDEV = tau * MDEV / np.sqrt(3)

    results.append({'tau': tau, 'MODIFIED ALLAN DEVIATION': MDEV, 'TIME DEVIATION': TDEV})
    print(f"Tau: {tau}, MDEV: {MDEV}, TDEV: {TDEV}")

# Create a DataFrame from the results
df = pd.DataFrame(results)

# Plot the MDEV and TDEV results
plt.figure(figsize=(8, 6))
plt.plot(df['tau'], df['MODIFIED ALLAN DEVIATION'], marker='o', linestyle='-', label='MDEV')
plt.plot(df['tau'], df['TIME DEVIATION'], marker='s', linestyle='--', label='TDEV')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Tau (s)')
plt.ylabel('Deviation')
plt.title('NPLI DO steered through NavIC CV')
plt.legend()
plt.grid(True)
plt.show()
