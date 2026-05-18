import numpy as np

# 1D array
a = np.array([1,2,3,4,5])

# ----Array operations----
b = np.array([10,20,30,40,50])
print(a+b)
print(a*b)

# --Python list operation for comparison with numpy----
a = [1,2,3,4,5]
b = [10,20,30,40,50]
print(a+b)

# ----2d Matrix------
matrix = np.array([[1,2,3],[4,5,6],[7,8,9]])
print(matrix)
print(matrix.shape)
print(matrix.ndim)
print(matrix.size)

#---CHALLENGE-----
def matrix_info(mat):
    print(f"SHape: {mat.shape}")
    print(f"Total elements: {mat.size}")
    print(f"Dimensions: {mat.ndim}")
    return

mat = np.array([[1,2,3],[4,5,6],[7,8,9]])
matrix_info(mat)  

