# Campus Cab Pooling System

A simple Python console application to manage cab sharing for college students. Students can submit ride requests, and when a cab is ready, the system automatically gives priority to senior students (higher college year) over juniors. If two students are in the same year, the one who requested first gets the seat.

Built using only Python 3 (standard library only, no extra packages to install).

---

## Project Files

- `main.py` - Contains the main menu and user interactions.
- `methods.py` - Defines the `RideRequest` and `Cab` classes.
- `storage.py` - Handles reading and writing data to JSON files.
- `cabs.json` - Stores information about all cabs (drivers, destinations, slots, and seats).
- `pending_requests.json` - Stores students who are currently waiting for a cab.

---

## How to Run

1. Open your terminal in this project folder.
2. Run the following command:

```bash
python3 main.py
```

---

## Menu Options

When you start the program, you will see this menu:

```text
----------------------------------------
       Campus Cab Pooling System
----------------------------------------
1. Add a student ride request
2. View waiting queue and cabs
3. Preview cab matches
4. Dispatch a cab
5. Save and exit
----------------------------------------
```

### What each option does:

1. **Add a student ride request:**
   Asks for student name, destination (`Delhi` or `Jaipur`), time slot (`Morning`, `Afternoon`, `Evening`, or `Night`), and college year (1 to 5). Adds the student to the waiting list and saves it.

2. **View waiting queue and cabs:**
   Shows all students currently waiting in priority order (seniors first). Also shows which cabs are available and which have already left.

3. **Preview cab matches:**
   Shows which students would get a seat in each open cab right now, without actually sending the cab.

4. **Dispatch a cab:**
   Lets you choose an open cab. The cab fills up with the highest-priority students waiting for that destination/time slot and then departs.

5. **Save and exit:**
   Saves any remaining changes to the JSON files and exits the program.

---

## How Priority Works

We use Python's built-in `heapq` (priority queue) module.

Each request in the queue is stored as:
`(-year, submitted_at, request)`

1. **Year Priority:** We use `-year` so that Year 5 students come first, followed by Year 4, 3, 2, and 1.
2. **Tie-Breaker:** If two students are in the same year, Python looks at `submitted_at`. The student who submitted earlier gets the seat first (first come, first served).

---

## Example Cab Data (`cabs.json`)

```json
[
  {
    "driver_name": "Vikram Rathore",
    "seats": 3,
    "destination": "Jaipur",
    "time_slot": "Morning",
    "has_left": false,
    "students": []
  },
  {
    "driver_name": "Harpreet Singh",
    "seats": 4,
    "destination": "Delhi",
    "time_slot": "Afternoon",
    "has_left": false,
    "students": []
  }
]
```

- **Valid Destinations:** `Delhi`, `Jaipur`
- **Valid Time Slots:** `Morning`, `Afternoon`, `Evening`, `Night`
- **Seats:** 1 to 4

---

## Why JSON Files?

- **Easy to read:** Anyone can open the `.json` files in a text editor to see or verify the data.
- **Safer than pickle:** Python's `pickle` module can execute hidden code when loading files, whereas JSON only stores plain text data.
- **Easy to reset:** You can easily clear or edit the files whenever you want to test with new data.
