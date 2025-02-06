import pytest
from project import add_expense, get_db_conn, remove_expense, parse_args
from unittest.mock import patch

def test_parse_args():
    # test basic input
    test_args = ["project.py", "-e", "100", "Food & Dining"]
    with patch("sys.argv", test_args):
        args = parse_args()
        assert args.expense == ["100", "Food & Dining"]
        
    # test verbose input
    test_args = ["project.py", "-e", "500", "household", "-r", "daily", "-ed", "2024-12-12", "-sd", "2024-12-31"]
    with patch("sys.argv", test_args):
        args = parse_args()
        assert args.expense == ["500", "household"]
        assert args.recurrence == "daily"
        assert args.start_date == "2024-12-31"
        assert args.end_date == "2024-12-12"
        
    # test invalid input
    test_args = ["project.py", "-invalidFlag"]
    with patch("sys.argv", test_args), pytest.raises(SystemExit) as exc_info:
        args = parse_args()
        assert exc_info.value.code == 2 
        
        
def test_add_expense():
    test_args = ["project.py", "-e", "100", "food"]
    with patch("sys.argv", test_args):
        assert add_expense(parse_args(), ":memory:") is True
    
    
    test_args = ["project.py", "-e", "100", "bazooka"]
    with patch("sys.argv", test_args):
        assert add_expense(parse_args(), ":memory:") is False
    
    
    test_args = ["project.py", "-e", "300", "household", "-r", "hourly", "-ed", "2025-12-12"]
    with patch("sys.argv", test_args):
        assert add_expense(parse_args(), ":memory:") is False
        
        
    test_args = ["project.py", "-e", "300", "household", "-r", "daily", "-ed", "2025-12-12"]
    with patch("sys.argv", test_args):
        assert add_expense(parse_args(), ":memory:") is True
        
        
def test_remove_expense():
    
    # adding an expense first
    insertion = ["project.py", "-e", "100", "food"]
    with patch("sys.argv", insertion):
        add_expense(parse_args(), ":memory:")
        
    # testing if it successfully removed
    test_args = ["project.py", "-rm", "1"]
    with patch("sys.argv", test_args):
        assert remove_expense(parse_args(), ":memory:") is True
    
    