from methods import RideRequest, cities, time_slots
from storage import load_cabs, save_cabs, load_requests, save_requests
import heapq


# Build the priority queue from the list of saved requests.
# Each item in the heap is: (-year, submitted_at, request)
# - Year is negative so higher years (seniors) come out first.
# - If years are equal, submitted_at is compared (earlier timestamp comes first).
def build_queue(pending_requests):
    trip_queue = {}
    for request in pending_requests:
        add_to_queue(request, trip_queue)
    return trip_queue


# Add a single request to the correct (destination, time_slot) heap.
def add_to_queue(request, trip_queue):
    key = (request.destination, request.time_slot)
    if key not in trip_queue:
        trip_queue[key] = []
    heapq.heappush(trip_queue[key], (-request.year, request.submitted_at, request))


# Option 1: Take user input and add a new ride request
def add_ride_request(trip_queue):
    print("\n----------------------------------------")
    print("         NEW RIDE REQUEST")
    print("----------------------------------------")

    name = input("Student name: ").strip()
    destination = input(f"Destination ({'/'.join(cities)}): ").strip()
    time_slot = input(f"Time slot ({'/'.join(time_slots)}): ").strip()

    try:
        year = int(input("College year (1 to 5): ").strip())
    except ValueError:
        print("\n[Error] Year must be a number between 1 and 5.")
        return

    try:
        request = RideRequest(
            student_name=name,
            destination=destination,
            time_slot=time_slot,
            year=year
        )
        add_to_queue(request, trip_queue)

        print("\n[Success] Ride request submitted successfully!")
        print(f"Student: {request.student_name} (Year {request.year})")
        print(f"Trip: {request.destination} - {request.time_slot}")

        # Save to pending_requests.json right away
        all_requests = []
        for queue in trip_queue.values():
            for entry in queue:
                all_requests.append(entry[-1])
        save_requests(all_requests)

    except ValueError as error:
        print(f"\n[Error] {error}")


# Option 2: View all waiting students and cabs
def view_status(trip_queue, cabs):
    print("\n========================================")
    print("        STUDENTS WAITING FOR CABS")
    print("========================================")

    all_requests = []
    for queue in trip_queue.values():
        for entry in queue:
            all_requests.append(entry[-1])

    # Sort students: senior years first, then earlier submission time
    all_requests.sort(key=lambda r: (-r.year, r.submitted_at))

    if not all_requests:
        print("No students are waiting right now.")
    else:
        print(f"Total students waiting: {len(all_requests)}\n")
        for i, req in enumerate(all_requests, start=1):
            print(f"{i}. {req.student_name} | Year {req.year} | {req.destination} ({req.time_slot}) | Submitted: {req.submitted_at}")

    print("\n========================================")
    print("               CAB STATUS")
    print("========================================")

    if not cabs:
        print("No cabs found.")
        return

    open_cabs = [c for c in cabs if not c.has_left]
    departed_cabs = [c for c in cabs if c.has_left]

    print(f"Available Cabs ({len(open_cabs)}):")
    if not open_cabs:
        print("  None available.")
    else:
        for i, cab in enumerate(open_cabs, start=1):
            free_seats = cab.seats - len(cab.students)
            print(f"  {i}. Driver: {cab.driver_name} | Route: {cab.destination} ({cab.time_slot}) | Free seats: {free_seats}/{cab.seats}")

    print(f"\nDeparted Cabs ({len(departed_cabs)}):")
    if not departed_cabs:
        print("  None have departed yet.")
    else:
        for i, cab in enumerate(departed_cabs, start=1):
            names = [s.student_name for s in cab.students]
            passengers = ", ".join(names) if names else "None"
            print(f"  {i}. Driver: {cab.driver_name} | Route: {cab.destination} ({cab.time_slot}) | Boarded: [{passengers}]")


# Option 3: Preview which students match open cabs (dry run)
def find_matches(trip_queue, cabs):
    print("\n========================================")
    print("             PREVIEW MATCHES")
    print("========================================")

    open_cabs = [c for c in cabs if not c.has_left]

    if not open_cabs:
        print("No open cabs to match.")
        return

    already_matched = []

    for i, cab in enumerate(open_cabs, start=1):
        free_seats = cab.seats - len(cab.students)
        print(f"\nCab {i}: {cab.driver_name} -> {cab.destination} [{cab.time_slot}]")
        print(f"Available seats: {free_seats}/{cab.seats}")

        if free_seats <= 0:
            print("  This cab is already full.")
            continue

        key = (cab.destination, cab.time_slot)
        queue = trip_queue.get(key, [])

        # Get sorted candidates who haven't already been picked in this preview
        sorted_entries = sorted(queue)
        candidates = []
        for entry in sorted_entries:
            student = entry[-1]
            if student not in already_matched and len(candidates) < free_seats:
                candidates.append(student)

        if not candidates:
            print("  No students waiting for this destination and time.")
        else:
            print("  Students who will get a seat (by priority):")
            for student in candidates:
                print(f"  - {student.student_name} (Year {student.year})")
                already_matched.append(student)


# Option 4: Pick a cab and dispatch it
def dispatch_cab(trip_queue, cabs):
    print("\n========================================")
    print("             DISPATCH A CAB")
    print("========================================")

    open_cabs = [c for c in cabs if not c.has_left]

    if not open_cabs:
        print("No open cabs available to dispatch.")
        return

    print("Choose an open cab to dispatch:")
    for i, cab in enumerate(open_cabs, start=1):
        free_seats = cab.seats - len(cab.students)
        print(f"{i}. {cab.driver_name} -> {cab.destination} [{cab.time_slot}] ({free_seats} seats free)")

    try:
        choice = int(input("\nEnter cab number (0 to cancel): ").strip())
    except ValueError:
        print("\n[Error] Please enter a valid number.")
        return

    if choice == 0:
        print("Dispatch cancelled.")
        return

    if choice < 1 or choice > len(open_cabs):
        print("\n[Error] Invalid choice.")
        return

    selected_cab = open_cabs[choice - 1]
    boarded_students = selected_cab.dispatch(trip_queue)

    print("\n----------------------------------------")
    print(f"Cab Dispatched: {selected_cab.driver_name}")
    print(f"Destination   : {selected_cab.destination} ({selected_cab.time_slot})")
    print(f"Seats filled  : {len(selected_cab.students)}/{selected_cab.seats}")
    print("----------------------------------------")

    if boarded_students:
        print("Students who boarded:")
        for s in boarded_students:
            print(f"- {s.student_name} (Year {s.year})")
    else:
        print("No students were waiting for this cab.")

    # Save changes to JSON files
    all_requests = []
    for queue in trip_queue.values():
        for entry in queue:
            all_requests.append(entry[-1])
    save_requests(all_requests)
    save_cabs(cabs)


# Main menu loop
def main():
    cabs = load_cabs()
    pending_requests = load_requests()
    trip_queue = build_queue(pending_requests)

    while True:
        print("\n----------------------------------------")
        print("       Campus Cab Pooling System")
        print("----------------------------------------")
        print("1. Add a student ride request")
        print("2. View waiting queue and cabs")
        print("3. Preview cab matches")
        print("4. Dispatch a cab")
        print("5. Save and exit")
        print("----------------------------------------")

        choice = input("Enter choice (1-5): ").strip()

        if choice == "1":
            add_ride_request(trip_queue)
        elif choice == "2":
            view_status(trip_queue, cabs)
        elif choice == "3":
            find_matches(trip_queue, cabs)
        elif choice == "4":
            dispatch_cab(trip_queue, cabs)
        elif choice == "5":
            save_cabs(cabs)
            all_requests = []
            for queue in trip_queue.values():
                for entry in queue:
                    all_requests.append(entry[-1])
            save_requests(all_requests)
            print("\nAll data saved. Goodbye!")
            print("\nHave a safe journey!")
            print("\nMade with love")
            break
        else:
            print("\n[Error] Please choose a number from 1 to 5.")


if __name__ == "__main__":
    main()
