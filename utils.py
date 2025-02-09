import shutil
import math
import sqlite3
import argparse
from termcolor import colored


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
        parser.error("The -sd/--start_date and -ed/--end_date flags require -r/--recurrence to be specified.")

    return args


def get_db_connection(db_path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
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
    conn.commit()
    return conn


def match_category(keyword) -> str:
    keyword = keyword.lower().strip()

    category_map = {
        "Food & Dining": ["food", "dining"],
        "Leisure & Shopping": ["leisure", "shopping", "shop"],
        "Transportation": ["transpo", "transportation"],
        "Family & Education": ["family", "education"],
        "Health & Wellness": ["health", "wellness"],
        "Household": ["household"],
        "Other": ["other"]
    }
    valid_keywords = sorted({kw for kws in category_map.values() for kw in kws})

    for category, keywords in category_map.items():
        if keyword in keywords:
            return category

    raise ValueError(
        f"Invalid category. Must be one of: {', '.join(valid_keywords)}"
    )


def get_message(amount, category):
    messages = {
        'Food & Dining':
            f"Moo-re food expense? Somebody’s eating good!\n Total: ${amount}. Don't forget dessert!",
        'Leisure & Shopping':
            f"Retail therapy is valid. Total: ${amount}.\n But remember, no refunds on impulse buys!",
        'Transportation':
            f"Gas, tickets, rides... this cow's got places to \nbe! Total: ${amount}. First class or hay cart?",
        'Household':
            f"Home sweet home... Total: ${amount}.\n Hope it comes with a 'mooortgage' discount!",
        'Family & Education':
            f"Investing in the herd? Love that for you\n! Total: ${amount}. Smart mooves!",
        'Health & Wellness':
            f"Treating yourself right! Iconic. Stay healthy, \nstay fabulous. Total: ${amount}",
        'Other':
            f"${amount} spent on miscellaneous, every detail \ncounts. Thanks for keeping track!",
    }
    return messages.get(category)


def pie_chart(labels, data) -> None:

    terminal_width, terminal_height = shutil.get_terminal_size()

    try:
        total = sum(data)
        percentages = [(val / total) * 100 for val in data]

        radius = min(terminal_height // 2 - 2, terminal_width // 4)
        center_x = terminal_width // 2
        center_y = terminal_height // 2

        colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

        # Draw
        current_angle = 0
        chart = [[' ' for _ in range(terminal_width)] for _ in range(terminal_height)]
        for i, (percentage, label) in enumerate(zip(percentages, labels)):
            angle = percentage * 3.6  # Convert percentage to degrees
            color = colors[i % len(colors)]

            for y in range(terminal_height):
                for x in range(0, terminal_width, 2):
                    dx = (x - center_x) / 2  # Compensate for character width
                    dy = y - center_y
                    distance = math.sqrt(dx**2 + dy**2)

                    if distance <= radius:
                        point_angle = math.degrees(math.atan2(dy, dx))
                        if point_angle < 0:
                            point_angle += 360

                        if current_angle <= point_angle < current_angle + angle:
                            chart[y][x] = colored('█', color)

            current_angle += angle

        # Print
        print("\nPie Chart:")
        for row in chart:
            print(''.join(char if char else ' ' for char in row))

        print("\033[1m" + "Legend:\n".center(terminal_width) + "\033[0m")
        for i, (label, percentage, data) in enumerate(zip(labels, percentages, data)):
            color = colors[i % len(colors)]
            legend_text = label.ljust(
                18) + f"({percentage:.1f}%): ".rjust(11) + f"${data:,}".ljust(9)
            print(colored(f"█ {legend_text}".center(terminal_width), color))

    except Exception as e:
        print(e)
