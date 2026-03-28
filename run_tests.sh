#!/bin/bash
#
# Test Runner Script for Online Quiz Assessment System
# This script provides convenient shortcuts for common testing tasks
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}Virtual environment not found!${NC}"
    exit 1
fi

# Function to display usage
show_usage() {
    echo -e "${BLUE}Online Quiz Assessment System - Test Runner${NC}"
    echo ""
    echo "Usage: ./run_tests.sh [command]"
    echo ""
    echo "Commands:"
    echo "  all           - Run all tests (parallel)"
    echo "  accounts      - Run accounts app tests"
    echo "  quiz          - Run quiz app tests"
    echo "  models        - Run all model tests"
    echo "  forms         - Run all form tests"
    echo "  views         - Run all view tests"
    echo "  utils         - Run utility tests"
    echo "  fast          - Run tests with --keepdb (faster)"
    echo "  coverage      - Run tests with coverage report"
    echo "  verbose       - Run tests with detailed output"
    echo "  single TEST   - Run a single test (e.g., single accounts.tests.TeacherProfileModelTest)"
    echo "  help          - Show this help message"
    echo ""
}

# Function to print section header
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"
}

# Function to run tests
run_test() {
    local description=$1
    shift
    print_header "$description"
    python manage.py test "$@"
    echo -e "\n${GREEN}✓ $description completed${NC}\n"
}

# Main command handling
case "${1:-all}" in
    all)
        run_test "Running All Tests (Parallel)" --parallel 4
        ;;
    
    accounts)
        run_test "Running Accounts App Tests" accounts -v 2
        ;;
    
    quiz)
        run_test "Running Quiz App Tests" quiz -v 2
        ;;
    
    models)
        print_header "Running All Model Tests"
        python manage.py test accounts.tests.TeacherProfileModelTest -v 2
        python manage.py test quiz.tests.QuizModelTest -v 2
        python manage.py test quiz.tests.QuestionGroupModelTest -v 2
        python manage.py test quiz.tests.QuestionModelTest -v 2
        python manage.py test quiz.tests.StudentSessionModelTest -v 2
        python manage.py test quiz.tests.AnswerModelTest -v 2
        python manage.py test quiz.tests.SuspiciousEventModelTest -v 2
        echo -e "\n${GREEN}✓ All model tests completed${NC}\n"
        ;;
    
    forms)
        print_header "Running All Form Tests"
        python manage.py test accounts.tests.TeacherRegistrationFormTest -v 2
        python manage.py test accounts.tests.LoginFormTest -v 2
        python manage.py test quiz.tests.QuizFormTest -v 2
        python manage.py test quiz.tests.StudentEntryFormTest -v 2
        echo -e "\n${GREEN}✓ All form tests completed${NC}\n"
        ;;
    
    views)
        print_header "Running All View Tests"
        python manage.py test accounts.tests.AccountViewsTest -v 2
        echo -e "\n${GREEN}✓ All view tests completed${NC}\n"
        ;;
    
    utils)
        run_test "Running Utility Tests" quiz.test_utils -v 2
        ;;
    
    fast)
        run_test "Running Tests (Fast Mode with --keepdb)" --parallel 4 --keepdb
        ;;
    
    coverage)
        print_header "Running Tests with Coverage"
        
        # Check if coverage is installed
        if ! python -c "import coverage" 2>/dev/null; then
            echo -e "${YELLOW}Installing coverage...${NC}"
            pip install coverage
        fi
        
        echo -e "${YELLOW}Running tests with coverage...${NC}\n"
        coverage run --source='.' manage.py test --parallel 4
        
        echo -e "\n${YELLOW}Generating coverage report...${NC}\n"
        coverage report -m
        
        echo -e "\n${YELLOW}Generating HTML coverage report...${NC}"
        coverage html
        
        echo -e "\n${GREEN}✓ Coverage report generated${NC}"
        echo -e "${GREEN}  View HTML report: open htmlcov/index.html${NC}\n"
        ;;
    
    verbose)
        run_test "Running Tests (Verbose Mode)" --parallel 4 -v 2
        ;;
    
    single)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please specify test path${NC}"
            echo "Example: ./run_tests.sh single accounts.tests.TeacherProfileModelTest"
            exit 1
        fi
        run_test "Running Single Test: $2" "$2" -v 2
        ;;
    
    help|--help|-h)
        show_usage
        ;;
    
    *)
        echo -e "${RED}Unknown command: $1${NC}\n"
        show_usage
        exit 1
        ;;
esac

# Test summary
if [ $? -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                               ║${NC}"
    echo -e "${GREEN}║           ALL TESTS PASSED ✓                  ║${NC}"
    echo -e "${GREEN}║                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                                               ║${NC}"
    echo -e "${RED}║           TESTS FAILED ✗                      ║${NC}"
    echo -e "${RED}║                                               ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════╝${NC}"
    exit 1
fi
