
fruits_append = ['apple', 'banana', 'cherry']
fruits_extend = ['apple', 'banana', 'cherry']

points = (1, 4, 5, 9)

fruits_append.append(points)
print(f"lunghezza append: {len(fruits_append)}")
print(f"fruits_append: {fruits_append}")

fruits_extend.extend(points)
print(f"lunghezza extend: {len(fruits_extend)}")
print(f"fruits_extend: {fruits_extend}")