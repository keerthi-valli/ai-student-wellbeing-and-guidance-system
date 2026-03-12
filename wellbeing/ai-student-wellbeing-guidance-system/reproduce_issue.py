from utils.mood_engine import calculate_mood_and_stress

cases = [
    ("I am happy about the weekend but I failed my exam and I feel terrible", "Sad"),
    ("I am happy normally but today is a disaster and I feel hopeless", "Sad"),
    ("Why is this happening to me? I feel so unlucky.", "Sad"),
    ("I am rejected by everyone.", "Sad"),
    ("I am happy", "Happy"),
]

neg = ["Sad", "Anxious", "Stressed", "Angry"]
pos = ["Happy", "Calm", "Excited"]

print("VERIFYING:")
fails = 0
for text, exp in cases:
    res = calculate_mood_and_stress(text)
    m = res["mood"]
    s = res["score"]
    
    passed = False
    if exp in neg and m in neg: passed = True
    elif exp in pos and m in pos: passed = True
    elif m == exp: passed = True
    
    status = "PASS" if passed else "FAIL"
    if not passed: fails += 1
    print(f"[{status}] '{text[:30]}...' -> Got: {m} (Score: {s})")

if fails == 0: print("ALL PASS")
else: print(f"{fails} FAILED")
