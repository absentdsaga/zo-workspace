#!/usr/bin/env python3
"""Check a meal/food string against nickel, histamine, and MRT-reactive lists.

Usage: python3 check-meal.py "grilled chicken with spinach and almonds"
"""
import sys
import re

HIGH_NICKEL = {
    "oat", "oatmeal", "wheat", "whole wheat", "whole grain", "rye", "millet",
    "buckwheat", "spelt", "bran", "granola", "muesli",
    "soy", "soybean", "tofu", "tempeh", "edamame", "soy milk", "soy sauce",
    "lentil", "chickpea", "hummus", "peanut", "peanut butter",
    "black bean", "kidney bean", "pinto bean", "navy bean", "lima bean",
    "almond", "hazelnut", "cashew", "pistachio", "walnut", "pecan",
    "sunflower seed", "sesame", "tahini", "flaxseed", "chia", "pumpkin seed",
    "chocolate", "cocoa", "nutella",
    "spinach", "kale", "brussels sprout", "broccoli", "green bean", "asparagus",
    "pea", "romaine", "tomato sauce", "tomato paste", "canned tomato",
    "mussel", "oyster", "clam", "shrimp",
    "licorice", "baking powder",
}

MODERATE_NICKEL = {"corn", "mushroom", "cauliflower", "cabbage", "banana",
                   "fig", "prune", "raisin", "beer", "red wine", "black tea"}

HIGH_HISTAMINE = {
    "aged cheese", "parmesan", "cheddar", "gouda", "blue cheese",
    "salami", "prosciutto", "bacon", "ham", "pepperoni",
    "sauerkraut", "kimchi", "kombucha", "miso", "soy sauce", "fish sauce",
    "vinegar", "pickle", "mustard", "ketchup", "mayo",
    "wine", "beer", "champagne", "alcohol",
    "leftover", "canned tuna", "sardine", "anchovy",
}

HISTAMINE_LIBERATOR = {
    "tomato", "strawberry", "citrus", "pineapple", "lemon", "lime", "orange",
    "chocolate", "egg white", "shellfish", "shrimp", "crab",
    "walnut", "cashew", "spinach", "eggplant",
}

MRT_REACTIVE = {
    "halibut": 5.1, "brussels sprout": 3.3, "kale": 2.9, "cow's milk": 2.9,
    "milk": 2.9, "peanut": 2.6, "msg": 2.5, "raspberry": 2.5, "yogurt": 2.4,
    "black bean": 2.3, "sage": 2.3, "cucumber": 2.2, "pistachio": 2.2,
    "kidney bean": 2.2, "cane sugar": 2.2, "pear": 2.2, "spelt": 2.2,
    "corn": 2.1, "radish": 2.1, "pinto bean": 2.1, "lemon": 2.1, "lime": 2.1,
    "rosemary": 2.1, "mustard": 2.1, "amaranth": 2.1, "walnut": 1.9,
    "chicken": 1.9, "lamb": 1.9, "eggplant": 1.8, "pumpkin": 1.8,
    "butternut squash": 1.8, "wheat": 1.8,
}

def check(meal):
    meal_lower = meal.lower()
    hits = {"nickel_high": [], "nickel_mod": [], "histamine_high": [],
            "histamine_lib": [], "mrt": []}

    for food in HIGH_NICKEL:
        if food in meal_lower:
            hits["nickel_high"].append(food)
    for food in MODERATE_NICKEL:
        if food in meal_lower:
            hits["nickel_mod"].append(food)
    for food in HIGH_HISTAMINE:
        if food in meal_lower:
            hits["histamine_high"].append(food)
    for food in HISTAMINE_LIBERATOR:
        if food in meal_lower:
            hits["histamine_lib"].append(food)
    for food, level in MRT_REACTIVE.items():
        if food in meal_lower:
            hits["mrt"].append(f"{food} ({level})")

    print(f"\nMeal: {meal}\n")

    any_hit = False
    if hits["nickel_high"]:
        any_hit = True
        print(f"  [HIGH NICKEL — AVOID] {', '.join(hits['nickel_high'])}")
    if hits["nickel_mod"]:
        any_hit = True
        print(f"  [moderate nickel — limit] {', '.join(hits['nickel_mod'])}")
    if hits["histamine_high"]:
        any_hit = True
        print(f"  [HIGH HISTAMINE] {', '.join(hits['histamine_high'])}")
    if hits["histamine_lib"]:
        any_hit = True
        print(f"  [histamine liberator] {', '.join(hits['histamine_lib'])}")
    if hits["mrt"]:
        any_hit = True
        print(f"  [MRT-reactive for Dioni] {', '.join(hits['mrt'])}")

    if not any_hit:
        print("  OK — no hits against nickel, histamine, or MRT lists.")
    else:
        severity = ("STOP — avoid this meal" if hits["nickel_high"] or
                    hits["histamine_high"] or
                    any(float(m.split('(')[1].rstrip(')')) >= 2.0 for m in hits["mrt"])
                    else "Caution — consider swapping flagged items")
        print(f"\n  Verdict: {severity}")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: check-meal.py '<meal description>'")
        sys.exit(1)
    check(" ".join(sys.argv[1:]))
