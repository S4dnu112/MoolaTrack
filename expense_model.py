from datetime import datetime


class Expense:
    RECUR_FREQUENCIES = ['daily', 'weekly', 'monthly', 'yearly']
    CATEGORIES = ['Food & Dining', 'Leisure & Shopping', 'Transportation',
                  'Household', 'Family & Education', 'Health & Wellness', 'Other']

    def __init__(
        self,
        base_amount: float,
        category: str,
        date_added: str,
        recurrence: str = "N/A",
        start_date: str = "N/A",
        end_date: str = "N/A",
        description: str = "N/A"
    ):
        self.base_amount = base_amount
        self.category = category
        self.date_added = date_added
        self.recurrence = recurrence
        self.start_date = start_date
        self.end_date = end_date
        self.description = description

    @property
    def base_amount(self):
        return self._base_amount

    @base_amount.setter
    def base_amount(self, base_amount):
        if base_amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self._base_amount = base_amount

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if category not in self.__class__.CATEGORIES:
            raise ValueError(
                f"Invalid category. Allowed categories: {', '.join(Expense.CATEGORIES)}")
        self._category = category

    @property
    def date_added(self):
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        if isinstance(date_added, str):
            Expense.validate_date(date_added)
        else:
            raise TypeError("date_added must be a string in 'YYYY-MM-DD' format")
        self._date_added = date_added

    @property
    def recurrence(self):
        return self._recurrence

    @recurrence.setter
    def recurrence(self, recurrence):
        if recurrence != "N/A" and recurrence not in Expense.RECUR_FREQUENCIES:
            raise ValueError(
                f"Invalid recurrence frequency. Allowed values: {', '.join(Expense.RECUR_FREQUENCIES)}")
        self._recurrence = recurrence

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, date):
        if self.recurrence is not False:
            Expense.validate_date(date)
        self._start_date = date

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, date):
        if self.recurrence is not False:
            Expense.validate_date(date)
        self._end_date = date

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def total_amount(self):
        if self.recurrence == "N/A":
            return self.base_amount

        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        date_now = datetime.now().date()
        parsed_date_added = datetime.strptime(self.date_added, "%Y-%m-%d").date()
        parsed_end_date = date_now if self.end_date == "N/A" else datetime.strptime(
            self.end_date, "%Y-%m-%d").date()

        start = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        end = date_now if parsed_end_date > date_now else parsed_end_date

        passed = end - start
        if passed.days < 0:
            return 0

        match(self.recurrence):
            case "daily":
                return (passed.days + 1) * self.base_amount
            case "weekly":
                return (passed.days // 7 + 1) * self.base_amount
            case "monthly":
                months_between = (end.year - start.year) * 12 + (end.month - start.month)
                if (end.day == days_in_month[end.month - 1] and end.day < start.day):
                    months_between += 1
                if end.day < start.day:
                    months_between -= 1
                return (months_between + 1) * self.base_amount
            case  "yearly":
                return ((end.year - start.year) + 1) * self.base_amount
            case _:
                raise ValueError(
                    "Invalid recurrence frequency. Allowed values are: daily, weekly, monthly, yearly.")

    def get_details(self):
        return [self.base_amount, self.category, self.date_added, self.recurrence, self.start_date, self.end_date, self.description]

    @staticmethod
    def headers():
        return ("ID", "Amount", "Category", "Date_Added", "Recurrence", "Start_Date", "End_Date", "Description", "Accumulated")

    @staticmethod
    def validate_date(date_string):
        try:
            if date_string != "N/A":
                datetime.strptime(date_string, "%Y-%m-%d")
            return date_string
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")
