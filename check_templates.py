import os

# Read the current file and check its state first
try:
    lines = open('templates/bookings/new.html', encoding='utf-8').readlines()
    print('Current line count:', len(lines))
    print('Line 1 preview:', lines[0][:80])
except Exception as e:
    print('Error reading file:', e)
