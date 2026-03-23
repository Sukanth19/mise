#!/usr/bin/env python3
"""Quick test to verify icalendar installation."""

try:
    import icalendar
    print(f"✓ icalendar is installed (version: {icalendar.__version__})")
    
    # Test basic functionality
    from icalendar import Calendar, Event
    from datetime import datetime
    
    cal = Calendar()
    cal.add('prodid', '-//Test//EN')
    cal.add('version', '2.0')
    
    event = Event()
    event.add('summary', 'Test Event')
    event.add('dtstart', datetime(2024, 1, 15, 12, 0, 0))
    event.add('dtend', datetime(2024, 1, 15, 13, 0, 0))
    
    cal.add_component(event)
    
    ical_data = cal.to_ical()
    
    if b'BEGIN:VCALENDAR' in ical_data and b'Test Event' in ical_data:
        print("✓ icalendar basic functionality works")
    else:
        print("✗ icalendar basic functionality failed")
        
except ImportError as e:
    print(f"✗ icalendar is NOT installed: {e}")
    print("\nTo install, run: pip install icalendar")
