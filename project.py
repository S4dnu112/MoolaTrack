from datetime import date
import sqlite3
import argparse

from tabulate import tabulate
import cowsay

from helpers import match_category, pie_chart
from expense_model import Expense


def main():
    db_url = 'database.db'
    args = parse_args()        

    print()
    if args.expense:
        add_expense(args, db_url)
    if args.summary:
        expense_summary(db_url)
    if args.all:
        expense_history(db_url)
    if args.remove:
        remove_expense(args.remove, db_url)  
    print()
    
    
def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter, 
        description='A Simple CLI Finance Tracker'
    )
    
    parser.add_argument(
        '-e', '--expense',
        nargs=2,
        metavar=('AMOUNT', 'CATEGORY'),
        help=(
            "Add an expense with an amount and category.\n"
            "Can be chained with the recurrence -r and description -d tag.\n"
            "Example: -e 250 Food -r monthly -d 'Groceries'\n"
        )
    )
    
    parser.add_argument(
        '-r', '--recurrence',
        type=str,
        choices=['daily', 'weekly', 'monthly', 'yearly'],
        help=(
            "Sets the recurrence frequency for an expense.\n"
            "Allowed values: daily, weekly, monthly, yearly.\n"
            "Can be used alone or with the --start_date and --end_date flags."
        )
    )

    parser.add_argument(
        '-sd', '--start_date',
        help=("Specifies the start date of the recurrence in YYYY-MM-DD format.\n"
              "Expense with recurrences defaults to date-added date if SD is not provided.")
    )

    parser.add_argument(
        '-ed', '--end_date',
        help=("Specifies the end date of the recurrence in YYYY-MM-DD format.\n"
              "Expense with recurrences have no end date if ED is not provided.")
    )
    
    parser.add_argument(
        '-d', '--description',
        type=str,
        help=(
            "Provide an optional description for the expense. Example: \"Dinner at a restaurant.\"\n"
            "Make sure to enclose the description in quotes."
        )
    )
    
    parser.add_argument(
        '-rm', '--remove',
        nargs=1,
        type=int,
        help=(
            "Remove a certain record based on ID."
        )
    )
    
    parser.add_argument(
        '-s', '--summary',
        help="Display a summary of your expenses.",
        action='store_true'
    )
    
    parser.add_argument(
        '-a', '--all',
        help="View all recorded expenses.",
        action='store_true'
    )

    args = parser.parse_args()
        
    if args.recurrence and not args.expense:
        parser.error("The -r/--recurrence flag can only be used with -e/--expense.")
    if args.description and not args.expense:
        parser.error("The -d/--description flag can only be used with -e/--expense.")
    if (args.start_date or args.end_date) and not args.recurrence:
        parser.error("The --start_date and --end_date flags require --recurrence to be specified.")

    return args


def add_expense(args, db_url) -> bool: 
    try:
        amount = float(args.expense[0])
        category = match_category(args.expense[1])
    except ValueError as e:
        cowsay.cow("Moo-stakes were made! Amount first,\n then category. (e.g., '42 food')\n|Moo-ve along now|")
        return False
    
    recurrence_details = [
        args.recurrence if args.recurrence else "N/A",
        args.start_date if args.start_date else "N/A",
        args.end_date if args.end_date else "N/A"
    ]
    description = args.description if args.description else "N/A"
    expense = Expense(amount, category, str(date.today()), *recurrence_details, description)

    try:
        with sqlite3.connect(db_url) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Amount REAL NOT NULL,
                    Category TEXT NOT NULL,
                    Date_Added TEXT NOT NULL,
                    Recurrence TEXT NOT NULL,
                    Start_Date TEXT NOT NULL,
                    End_Date TEXT NOT NULL,
                    Description TEXT NOT NULL
                )
            ''')        
            cursor.execute('''
                INSERT INTO expenses (Amount, Category, Date_Added, Recurrence, Start_Date, End_Date, Description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', expense.get_details())
            
        cowsay.cow(f"Mooolah spent in {expense.category}! Total: ${expense.total_amount}. Udderly recorded! 🐄💸")
        return True
    except sqlite3.Error as e:
        cowsay.cow(f"Database error: {str(e)}")
        return False


def remove_expense(id, db_url) -> bool: 
    try:
        with sqlite3.connect(db_url) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM expenses WHERE ID = ?', (id))
            
            if cursor.rowcount > 0:
                cowsay.tux(f"Expense with ID {id} has slipped away! Consider it deleted. Waddle on!")
                return True
            else:
                raise sqlite3.OperationalError
            
    except sqlite3.OperationalError as e:
        cowsay.tux(f"No expense found with ID {id}!")
        return False
    except sqlite3.Error as e:
        cowsay.tux(f"Database error: {str(e)}")
        return False


def expense_history(db_url) -> bool:
    try:
        with sqlite3.connect(db_url) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM expenses')
            table = list(cursor.fetchall())
            table.reverse()
        
        if table:
            print(tabulate(table, headers=Expense.headers(), tablefmt='fancy_grid'))    
            return True
        else:
            raise sqlite3.OperationalError
    except sqlite3.Error as e:
        cowsay.cow(f"Moo! It seems the expense barn is empty. Time to add some moo-lah!")
        return False
    
        
def expense_summary(db_url) -> bool: 
    values = {
        'Food & Dining': 0,
        'Leisure & Shopping': 0,
        'Transportation': 0,
        'Household': 0,
        'Family & Education': 0,
        'Health & Wellness': 0,
        'Other': 0
    }
    
    try:
        with sqlite3.connect(db_url) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT Amount, Category, Date_Added, Recurrence, Start_Date, End_Date, Description 
                FROM expenses
            ''')
            expenses = [Expense(*row) for row in cursor.fetchall()]
            
        if not expenses:
            raise sqlite3.OperationalError
            
        for expense in expenses:
            values[expense.category] += expense.total_amount
            
        pie_chart(values.keys(), values.values())
        return True
    
    
    except sqlite3.OperationalError as e:
        cowsay.tux("I searched high and low... and found absolutely nothing!")  

    except sqlite3.Error as e:
        cowsay.tux(f"Database error: {str(e)}")
        return False
    
    
if __name__ == "__main__":
    main()