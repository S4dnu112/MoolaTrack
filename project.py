from datetime import date
from tabulate import tabulate
import cowsay

from utils import match_category, pie_chart, get_db_connection, parse_args, get_message
from expense_model import Expense


def main():
    args = parse_args()
    db_connection = get_db_connection('database.db')

    print()

    if args.expense:
        try:
            amount, category = add_expense(args, db_connection)
            cowsay.cow(get_message(amount, category))
        except ValueError as e:
            cowsay.cow(e)
        except Exception as e:
            cowsay.cow(f"Error: {e}")

    if args.remove:
        try:
            id = args.remove
            remove_expense(id, db_connection)
            cowsay.tux(f"Expense with ID {id} has slipped away! \nConsider it deleted. Waddle on!")
        except ValueError:
            cowsay.tux(f"I searched high and low... and found absolutely \nnothing!")
        except Exception as e:
            cowsay.cow(f"Error: {e}")

    if args.all:
        try:
            table = expense_history(db_connection)
            print(tabulate(table, headers=Expense.headers(), tablefmt='fancy_grid'))
        except ValueError:
            cowsay.cow(f"... Maybe, the cows ate the database?")
        except Exception as e:
            cowsay.cow(f"Error: {e}")

    if args.summary:
        try:
            expense_map = expense_summary(db_connection)
            pie_chart(expense_map.keys(), expense_map.values())
        except ValueError:
            cowsay.cow("... Maybe, the cows ate the database?")
        except Exception as e:
            cowsay.cow(f"Error: {e}")

    print()


def add_expense(args, db_conn) -> list:
    try:
        amount = float(args.expense[0])
    except ValueError:
        raise ValueError("Moo-stakes were made! Amount first,\n then category. (e.g., '42 food')")

    category = match_category(args.expense[1])

    recurrence_details = [
        args.recurrence if args.recurrence else "N/A",
        args.start_date if args.start_date else "N/A",
        args.end_date if args.end_date else "N/A"
    ]
    if args.recurrence and args.start_date == "N/A":
        args.start_date = str(date.today())

    description = args.description if args.description else "N/A"
    expense = Expense(amount, category, str(date.today()), *recurrence_details, description)

    with db_conn:
        cursor = db_conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (Amount, Category, Date_Added, Recurrence, Start_Date, End_Date, Description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', expense.get_details())

    return [expense.total_amount, category]


def remove_expense(id, db_conn) -> int:
    with db_conn:
        cursor = db_conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE ID = ?', (id,))

        if cursor.rowcount > 0:
            return id
    raise ValueError


def expense_history(db_conn) -> list[list]:
    with db_conn:
        cursor = db_conn.cursor()
        cursor.execute('SELECT * FROM expenses')
        table = cursor.fetchall()

        if not table:
            raise ValueError("No expenses found in the database.")

    updated_table = []
    for row in table:
        expense = Expense(*row[1:])
        updated_row = list(row) + [expense.total_amount]
        updated_table.append(updated_row)

    updated_table.reverse()
    return updated_table


def expense_summary(db_conn) -> dict:
    expense_map = {
        'Food & Dining': 0,
        'Leisure & Shopping': 0,
        'Transportation': 0,
        'Household': 0,
        'Family & Education': 0,
        'Health & Wellness': 0,
        'Other': 0
    }
    with db_conn:
        cursor = db_conn.cursor()
        cursor.execute('''
            SELECT Amount, Category, Date_Added, Recurrence, Start_Date, End_Date, Description
            FROM expenses
        ''')
        expenses = [Expense(*row) for row in cursor.fetchall()]
        if not expenses:
            raise ValueError

    for expense in expenses:
        expense_map[expense.category] += expense.total_amount
    return expense_map


if __name__ == "__main__":
    main()
