
import csv
import os
from datetime import date, datetime, timedelta

HISTORY_FILE = "expenses.csv"
FIELDS = ["date", "item", "price", "category"]
def add_expense(item: str, price: float, category: str) -> None:
    """Append one purchase to the history file with today's date."""
    file_exists = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(FIELDS)
        writer.writerow([date.today().isoformat(), item, f"{price:.2f}", category])


def load_expenses() -> list[dict]:
    """Read every saved entry. Returns [] if there is no history yet."""
    if not os.path.exists(HISTORY_FILE):
        return []
    expenses = []
    with open(HISTORY_FILE, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                expenses.append({
                    "date": datetime.strptime(row["date"], "%Y-%m-%d").date(),
                    "item": row["item"],
                    "price": float(row["price"]),
                    "category": row["category"],
                })
            except (ValueError, KeyError):
                continue
    return expenses

def total_between(start: date, end: date) -> float:
    """Sum prices for entries with start <= date <= end."""
    return sum(e["price"] for e in load_expenses() if start <= e["date"] <= end)


def weekly_total() -> float:
    """Spending over the last 7 days (today included)."""
    today = date.today()
    return total_between(today - timedelta(days=6), today)


def monthly_total() -> float:
    """Spending from the 1st of the current month through today."""
    today = date.today()
    return total_between(today.replace(day=1), today)


def category_breakdown(start: date, end: date) -> dict[str, float]:
    """Bonus: totals per category in a date range."""
    totals: dict[str, float] = {}
    for e in load_expenses():
        if start <= e["date"] <= end:
            totals[e["category"]] = totals.get(e["category"], 0) + e["price"]
    return totals
def prompt_expense() -> None:
    item = input("Item name: ").strip()
    while not item:
        item = input("Item name can't be empty: ").strip()

    while True:
        try:
            price = float(input("Price: ").strip())
            if price < 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a valid positive number (e.g. 4.50).")

    category = input("Category (e.g. Food, Transport): ").strip() or "Other"

    add_expense(item, price, category)
    print(f"Saved: {item} - {price:.2f} [{category}]")


def main() -> None:
    while True:
        print("\n1) Add expense  2) Weekly total  3) Monthly total  4) Quit")
        choice = input("> ").strip()
        if choice == "1":
            prompt_expense()
        elif choice == "2":
            print(f"Last 7 days: {weekly_total():.2f}")
        elif choice == "3":
            print(f"This month: {monthly_total():.2f}")
        elif choice == "4":
            break
        else:
            print("Please choose 1-4.")


if __name__ == "__main__":
    main()
