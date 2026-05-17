def square_evens(numbers):
    results = [n**2 for n in numbers if n%2==0]
    return results
data = [5,6,10,16,4,90]
print(square_evens(data))  
