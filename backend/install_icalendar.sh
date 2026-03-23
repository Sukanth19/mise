#!/bin/bash
# Install icalendar library for meal plan iCal export

echo "Installing icalendar library..."
pip install icalendar>=5.0.0

echo "Verifying installation..."
python -c "import icalendar; print('icalendar version:', icalendar.__version__)"

echo "Installation complete!"
