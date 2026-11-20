"""Single source of truth for the model's input columns.

CSV order is: time, v1..v28, amount (target 'class' is separate).
Training and the API both import from here, so they cannot disagree.
"""

FEATURES = ["time"] + [f"v{i}" for i in range(1, 29)] + ["amount"]
TARGET = "class"
SCALE_COLS = ["time", "amount"]
