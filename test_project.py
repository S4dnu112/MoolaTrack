import pytest
from utils import parse_args, get_db_connection
from project import add_expense, remove_expense, expense_history, expense_summary
from unittest.mock import patch


@pytest.fixture(scope="module")
def persistent_db():
    return get_db_connection(":memory:")


def test_parse_args():
    with patch("sys.argv", ["project.py", "-e", "100", "food"]):
        args = parse_args()
        assert args.expense == ["100", "food"]

    test_args = ["project.py", "-e", "500", "household", "-r",
                 "daily", "-sd", "2024-12-12", "-ed", "2024-12-31"]
    with patch("sys.argv", test_args):
        args = parse_args()
        assert args.expense == ["500", "household"]
        assert args.recurrence == "daily"
        assert args.start_date == "2024-12-12"
        assert args.end_date == "2024-12-31"

    test_args = ["project.py", "--invalidFlag"]
    with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
        parse_args()
    assert exc_info.value.code == 2


def test_add_expense(persistent_db):
    # id 1
    test_args = ["project.py", "-e", "100", "food"]
    with patch("sys.argv", test_args):
        assert add_expense(parse_args(), persistent_db) == [100.0, 'Food & Dining']

    # id 2
    test_args = ["project.py", "-e", "300", "household", "-r",
                 "daily", "-sd", "2025-01-01", "-ed", "2025-01-02"]
    with patch("sys.argv", test_args):
        assert add_expense(parse_args(), persistent_db) == [600.0, "Household"]

    with patch("sys.argv", ["project.py", "-e", "100", "bazooka"]):
        with pytest.raises(ValueError):
            add_expense(parse_args(), persistent_db)

    with patch("sys.argv", ["project.py", "-e", "300", "household", "-r", "hourly", "-ed", "2025-12-12"]):
        with pytest.raises(ValueError):
            add_expense(parse_args(), persistent_db)


def test_remove_expense(persistent_db):
    with patch("sys.argv", ["project.py", "-rm", "2"]):
        assert remove_expense(parse_args().remove, persistent_db) == 2

    with patch("sys.argv", ["project.py", "-rm", "5"]), pytest.raises(ValueError):
        assert remove_expense(parse_args().remove, persistent_db)


def test_expense_history(persistent_db):
    with patch("sys.argv", ["project.py", "-a"]):
        assert isinstance(expense_history(persistent_db), list)

        with pytest.raises(ValueError):
            expense_history(get_db_connection(":memory:"))


def test_expense_summary(persistent_db):
    with patch("sys.argv", ["project.py", "-s"]):
        assert isinstance(expense_summary(persistent_db), dict)

        with pytest.raises(ValueError):
            expense_history(get_db_connection(":memory:"))
