import numpy as np

a = np.array([(1, 2, 3), (4, -1, 5), (10, 11, 12),
              (8, 8, 8), (7, -4, 6), (2, 2, 0)], dtype=float)
x = np.array([(2, ), (11, ), (-1, )], dtype=float)


print(a @ x)

# with open('smallX.dat', 'w') as file:
#     matrix = x
#     file.write(str(matrix.shape[0]) + '\n')
#     file.write(str(matrix.shape[1]) + '\n')

#     for d in matrix.flatten():
#         file.write(str(d) + '\n')
