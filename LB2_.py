import tkinter as tk
import numpy as np
import pandas as pd

def function_for_users(T, n, r0, vol, E1, E2):
    
    u = np.exp(vol*np.sqrt(T/n))
    d = 1/u
    p = (np.exp(r0*T/n)-d)/(u - d)
    q = 1-p
    
    zero_massiv = np.zeros((n+1, n+1))
    zero_massiv[0,0] = 5
    for i in range(1, n+1):
        zero_massiv[i, 0] = round(zero_massiv[i-1,0]*d, 2)
    for i in range(1, n+1):
        for j in range(1, i+1):
            zero_massiv[i,j] = round(zero_massiv[i,j-1]*u**2, 2)
    
    # ZCB10
    zero_massiv2 = np.zeros((n+1, n+1))
    zero_massiv2[-1,:] = 100
    for i in range(n):
        for j in range(n-i):
            zero_massiv2[n-i-1,j] = round(((zero_massiv2[n-i, j]/100*q + zero_massiv2[n-i, j+1]/100*p)/(1+zero_massiv[n-i-1,j]/100))*100, 2)
    
    # форвард на бескупонную облигацию, который исполняется в момент времени t=5
    k = 5
    zero_massiv3 = np.zeros((k+1, k+1))
    zero_massiv3[-1,:] = 100
    for i in range(k):
        for j in range(k-i):
            zero_massiv3[k-i-1,j] = round(((zero_massiv3[k-i, j]/100*q + zero_massiv3[k-i, j+1]/100*p)/(1+zero_massiv[k-i-1,j]/100))*100, 2)
    
    Ft = zero_massiv2[0,0]/zero_massiv3[0,0]*100
    
    # Цена фьючерса на бескупонную облигацию ZCB10, в момент времени t=5
    zero_massiv4 = np.zeros((k+1, k+1))
    zero_massiv4[-1] = zero_massiv2[5, :k+1]
    for i in range(k):
        for j in range(k-i):
            zero_massiv4[k-i-1,j] = round((zero_massiv4[k-i, j]*q + zero_massiv4[k-i, j+1]*p), 2)
    
    # Американский опцион на фьючерс на ZCB10
    zero_massiv5 = np.zeros((k+1, k+1))
    for i in range(k+1):
        zero_massiv5[-1, i] = max(0, zero_massiv2[k, i]-E1)
    for i in range(k):
        for j in range(k-i):
            zero_massiv5[k-i-1,j] = round(max(max(0, zero_massiv2[k-i-1,j]-E1), (zero_massiv5[k-i, j]*q + zero_massiv5[k-i, j+1]*p)/np.exp(r0*T/n)), 2)
    
    zero_massiv6 = np.zeros((k+1, k+1))
    for i in range(k+1):
        zero_massiv6[-1, i] = max(0, zero_massiv2[k, i]-E2)
    for i in range(k):
        for j in range(k-i):
            zero_massiv6[k-i-1,j] = round(max(max(0, zero_massiv2[k-i-1,j]-E2), (zero_massiv6[k-i, j]*q + zero_massiv6[k-i, j+1]*p)/np.exp(r0*T/n)), 2)
    
    return zero_massiv2[0,0], Ft, zero_massiv4[0,0], zero_massiv5[0,0], zero_massiv6[0,0]


# Создаем интерфейс
root = tk.Tk()
root.title("Финансовый калькулятор")
root.geometry("350x450")

# Переменные
T_var = tk.StringVar(value="10")
n_var = tk.StringVar(value="10")
r0_var = tk.StringVar(value="0.05")
vol_var = tk.StringVar(value="0.1")
E1_var = tk.StringVar(value="70")
E2_var = tk.StringVar(value="80")
result_var = tk.StringVar()

def update(*args):
    try:
        T = float(T_var.get())
        n = int(n_var.get())
        r0 = float(r0_var.get())
        vol = float(vol_var.get())
        E1 = float(E1_var.get())
        E2 = float(E2_var.get())
        
        res = function_for_users(T, n, r0, vol, E1, E2)
        
        result_var.set(f"ZCB10: {res[0]:.2f} %\n"
                      f"Форвард: {res[1]:.2f} %\n"
                      f"Фьючерс: {res[2]:.2f} %\n"
                      f"Опцион E1: {res[3]:.2f} %\n"
                      f"Опцион E2: {res[4]:.2f} %")
    except ValueError as e:
        result_var.set(f"Ошибка: проверьте данные\n{str(e)}")
    except Exception as e:
        result_var.set(f"Ошибка: {str(e)}")

# Привязываем обновление к изменениям в полях
for var in [T_var, n_var, r0_var, vol_var, E1_var, E2_var]:
    var.trace('w', update)

# Создаем поля ввода
row = 0
fields = [
    ("T (время):", T_var),
    ("n (шаги):", n_var),
    ("r0 (ставка):", r0_var),
    ("vol (волатильность):", vol_var),
    ("E1 (страйк 1):", E1_var),
    ("E2 (страйк 2):", E2_var)
]

for label, var in fields:
    tk.Label(root, text=label, font=('Arial', 10)).grid(row=row, column=0, pady=5, padx=10, sticky='e')
    tk.Entry(root, textvariable=var, width=15, font=('Arial', 10)).grid(row=row, column=1, pady=5)
    row += 1

# Добавляем разделитель
tk.Label(root, text="-" * 30).grid(row=row, column=0, columnspan=2, pady=10)
row += 1

# Результаты
tk.Label(root, text="Результаты:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, pady=5)
row += 1

result_label = tk.Label(root, textvariable=result_var, justify=tk.LEFT, 
                        bg="lightgray", relief=tk.SUNKEN, 
                        padx=10, pady=10, font=('Courier', 9))
result_label.grid(row=row, column=0, columnspan=2, pady=5, padx=10, sticky='ew')


update()

root.mainloop()