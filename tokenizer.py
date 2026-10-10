import math
import multiprocessing
import random

with open("wiki.test.txt", "r",encoding="utf-8") as f:
    data = list(f.read())
    # 1279333 characters, 157 unique characters, 1279332 consecutive pairs.


# Pair Node Object for the linked list in hash table
class Node():
    def __init__(self,pair):
        self.pair = pair
        self.prev = None
        self.next = None

class Hashmap():
    def __init__(self, initial_capacity=8):
        self.capacity = initial_capacity
        self.buckets = [None] * self.capacity
        self.size = 0  

    def hash(self,pair):
        h = 0
        for char in str(pair):
            h = (h*31 + ord(char))  & 0xFFFFFFFF
        
