

# update your packages
sudo apt-get update && sudo apt-get upgrade

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found. Please install Python 3."
    exit 1
fi

# Check for Python 3.10 version and above
PYTHON_VERSION=$(python3 -V | cut -d ' ' -f 2) # Extract the Python version
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
    echo "Python 3.10 or greater is required. Found Python $PYTHON_VERSION. Please upgrade Python."
    exit 1
fi

# Check for Pip
if ! command -v pip &> /dev/null; then
    echo "Pip could not be found. Installing Pip. You might be asked for your password."
    sudo apt install python3-pip
    if [ $? -ne 0 ]; then
        echo "Failed to install pip. Exiting..."
        exit 1
    fi
fi

sudo apt install python3.10-venv



# Create a virtual environment using venv
python3 -m venv venv

# Check if venv was created successfully
if [ ! -d "venv" ]; then
    echo "Failed to create a virtual environment. Exiting..."
    exit 1
fi

# Activate the virtual environment
source venv/bin/activate

# Confirm venv activation by checking for VIRTUAL_ENV env variable
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment failed to activate. Exiting..."
    exit 1
fi

# Ensure pip is up to date
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt


python3 tests/load_test/load-test.py
