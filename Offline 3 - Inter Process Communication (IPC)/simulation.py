import pygame
import random
import asyncio
import platform
from enum import Enum
from collections import deque

# Constants
LAMBDA = 10000.234
NUM_STATIONS = 4
MAX_ARRIVAL_DELAY = 6
SLEEP_MULTIPLE = 1000000  # Simulated in microseconds
PERIODICITY = 10
FPS = 15  # Reduced FPS for better log visibility

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Simulation parameters
num_operatives = 15
unit_size = 3
document_recreation_interval = 5  # seconds
logbook_entry_interval = 3  # seconds
operations_completed = 0
reader_count = 0

# Screen setup
WIDTH = 1000
HEIGHT = 600
STATION_WIDTH = 100
STATION_HEIGHT = 50
OPERATIVE_RADIUS = 20
LOGBOOK_WIDTH = 100
LOGBOOK_HEIGHT = 50
LOG_HEIGHT = 200
QUEUE_OFFSET = 40  # Vertical spacing for queued operatives

# Simulation state
class TypewritingState(Enum):
    FREE = 0
    OCCUPIED = 1

class OperativeState(Enum):
    ARRIVING = 0
    WAITING_FOR_RECREATING = 1
    RECREATING = 2
    RECREATED = 3
    WAITING_FOR_LOGBOOK = 4
    LOGBOOK_ENTRY = 5

class TypewritingStation:
    def __init__(self, id):
        self.id = id
        self.state = TypewritingState.FREE
        self.rect = pygame.Rect(50 + (id - 1) * 150, 100, STATION_WIDTH, STATION_HEIGHT)
        self.queue = deque()  # Queue for operatives waiting to use this station

class Operative:
    def __init__(self, id):
        self.id = id
        self.unit_id = (id - 1) // unit_size + 1
        self.typewriting_station_id = id % NUM_STATIONS + 1
        self.state = OperativeState.ARRIVING
        self.arrival_delay = random.randint(1, MAX_ARRIVAL_DELAY)
        self.is_leader = (id % unit_size == 0)
        self.pos = [50 + (id - 1) * 50, 300]  # Starting position
        self.target_pos = self.pos.copy()
        self.start_time = pygame.time.get_ticks() / 1000.0

class Unit:
    def __init__(self, id):
        self.id = id
        self.leader_id = id * unit_size
        self.typewriting_completion_count = 0

    def typewriting_done(self):
        return self.typewriting_completion_count == unit_size

    def increment_typewriting_completion_count(self):
        self.typewriting_completion_count += 1

# Global state
typewriting_stations = [TypewritingStation(i) for i in range(1, NUM_STATIONS + 1)]
operatives = [Operative(i) for i in range(1, num_operatives + 1)]
units = [Unit(i) for i in range(1, num_operatives // unit_size + 1)]
logbook_rect = pygame.Rect(WIDTH - 150, 50, LOGBOOK_WIDTH, LOGBOOK_HEIGHT)
logbook_queue = deque()  # Queue for leaders waiting to access logbook
log_messages = deque(maxlen=15)  # Increased for better visibility
reader1_pos = [WIDTH - 50, 150]
reader2_pos = [WIDTH - 50, 200]
reader1_active = False
reader2_active = False
reader1_next_time = (MAX_ARRIVAL_DELAY / 5)
reader2_next_time = random.randint(1, MAX_ARRIVAL_DELAY)
station_locks = [False] * NUM_STATIONS
logbook_locked = False

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Operative Simulation")
font = pygame.font.SysFont('arial', 16)
clock = pygame.time.Clock()

def elapsed_time_sec():
    return pygame.time.get_ticks() / 1000.0

def show_details(message):
    log_messages.append((message, elapsed_time_sec()))

def notify_document_recreation_end(operative_id):
    station_id = operatives[operative_id - 1].typewriting_station_id
    waiters = list(typewriting_stations[station_id - 1].queue)
    waiters_str = " ".join(map(str, waiters))
    show_details(f"{GREEN}Operative {operative_id} has notified document recreation end at time {elapsed_time_sec():.1f}. Waiting operatives at station {station_id}: {waiters_str}")

def operative_arrival(op):
    if elapsed_time_sec() - op.start_time >= op.arrival_delay:
        op.state = OperativeState.WAITING_FOR_RECREATING
        station = typewriting_stations[op.typewriting_station_id - 1]
        station.queue.append(op.id)
        # Position in queue (below station)
        queue_index = list(station.queue).index(op.id)
        op.target_pos = [50 + (op.typewriting_station_id - 1) * 150 + STATION_WIDTH // 2, 100 + STATION_HEIGHT + (queue_index + 1) * QUEUE_OFFSET]
        show_details(f"Operative {op.id} [from unit {op.unit_id}] has arrived at typewriting station {op.typewriting_station_id} at time {elapsed_time_sec():.1f}")

def document_recreation_start(op):
    station = typewriting_stations[op.typewriting_station_id - 1]
    if station.queue and station.queue[0] == op.id and not station_locks[op.typewriting_station_id - 1]:
        station_locks[op.typewriting_station_id - 1] = True
        station.state = TypewritingState.OCCUPIED
        station.queue.popleft()  # Remove from queue
        op.state = OperativeState.RECREATING
        op.target_pos = [50 + (op.typewriting_station_id - 1) * 150 + STATION_WIDTH // 2, 100 + STATION_HEIGHT]
        op.start_time = elapsed_time_sec()
        # Update positions of remaining operatives in queue
        for i, op_id in enumerate(station.queue):
            operatives[op_id - 1].target_pos = [50 + (op.typewriting_station_id - 1) * 150 + STATION_WIDTH // 2, 100 + STATION_HEIGHT + (i + 1) * QUEUE_OFFSET]

def document_recreation_end(op):
    if op.state == OperativeState.RECREATING and elapsed_time_sec() - op.start_time >= document_recreation_interval:
        op.state = OperativeState.RECREATED
        unit = units[op.unit_id - 1]
        unit.increment_typewriting_completion_count()
        show_details(f"{GREEN}Operative {op.id} [from unit {op.unit_id}] has completed document recreation at typewriting station {op.typewriting_station_id} at time {elapsed_time_sec():.1f}")
        notify_document_recreation_end(op.id)
        show_details(f"{RED}Operative {op.id} [from unit {op.unit_id}] handed over document {unit.typewriting_completion_count} to the leader of unit {op.unit_id} at time {elapsed_time_sec():.1f}")
        station_locks[op.typewriting_station_id - 1] = False
        typewriting_stations[op.typewriting_station_id - 1].state = TypewritingState.FREE
        op.target_pos = [50 + (op.id - 1) * 50, 300]  # Return to waiting area
        # Update positions of remaining operatives in queue
        station = typewriting_stations[op.typewriting_station_id - 1]
        station_locks[op.typewriting_station_id - 1] = False
        for i, op_id in enumerate(station.queue):
            operatives[op_id - 1].target_pos = [50 + (op.typewriting_station_id - 1) * 150 + STATION_WIDTH // 2, 100 + STATION_HEIGHT + (i + 1) * QUEUE_OFFSET]

def logbook_entry(op):
    global operations_completed, logbook_locked
    if op.state == OperativeState.WAITING_FOR_LOGBOOK and logbook_queue and logbook_queue[0] == op.id and not logbook_locked:
        logbook_queue.popleft()  # Remove from queue
        logbook_locked = True
        op.state = OperativeState.LOGBOOK_ENTRY
        op.target_pos = [WIDTH - 150 + LOGBOOK_WIDTH // 2, 100]  # Move to logbook
        op.start_time = elapsed_time_sec()
        show_details(f"{BLUE}Unit {op.unit_id} has started intelligence distribution at time {elapsed_time_sec():.1f}")
        # Update positions of remaining operatives in logbook queue
        for i, op_id in enumerate(logbook_queue):
            operatives[op_id - 1].target_pos = [WIDTH - 150 + LOGBOOK_WIDTH // 2, 100 + LOGBOOK_HEIGHT + (i + 1) * QUEUE_OFFSET]
    elif op.state == OperativeState.LOGBOOK_ENTRY and elapsed_time_sec() - op.start_time >= logbook_entry_interval:
        show_details(f"{BLUE}Unit {op.unit_id} has completed intelligence distribution at time {elapsed_time_sec():.1f}")
        operations_completed += 1
        logbook_locked = False
        op.state = OperativeState.RECREATED
        op.target_pos = [50 + (op.id - 1) * 50, 300]  # Return to waiting area
        # Update positions of remaining operatives in logbook queue
        for i, op_id in enumerate(logbook_queue):
            operatives[op_id - 1].target_pos = [WIDTH - 150 + LOGBOOK_WIDTH // 2, 100 + LOGBOOK_HEIGHT + (i + 1) * QUEUE_OFFSET]

def intelligent_stuff_1():
    global reader_count, reader1_active, reader1_next_time, logbook_locked
    if elapsed_time_sec() >= reader1_next_time and not reader1_active:
        reader_count += 1
        if reader_count == 1:
            logbook_locked = True
        reader1_active = True
        show_details(f"Intelligent stuff 1 has begun reviewing logbook at time {elapsed_time_sec():.1f}. Operations completed = {operations_completed}")
        reader1_pos[1] = 100  # Move to logbook
        reader1_next_time = elapsed_time_sec() + 0.5
    elif reader1_active and elapsed_time_sec() >= reader1_next_time:
        reader_count -= 1
        if reader_count == 0:
            logbook_locked = False
        show_details(f"Intelligent stuff 1 has finished reviewing logbook at time {elapsed_time_sec():.1f}. Operations completed = {operations_completed}")
        show_details(f"Intelligent stuff 1 is calling Shelby bhai at time {elapsed_time_sec():.1f}")
        reader1_active = False
        reader1_pos[1] = 150  # Move back
        reader1_next_time = elapsed_time_sec() + PERIODICITY

def intelligent_stuff_2():
    global reader_count, reader2_active, reader2_next_time, logbook_locked
    if elapsed_time_sec() >= reader2_next_time and not reader2_active:
        reader_count += 1
        if reader_count == 1:
            logbook_locked = True
        reader2_active = True
        show_details(f"Intelligent stuff 2 has begun reviewing logbook at time {elapsed_time_sec():.1f}. Operations completed = {operations_completed}")
        reader2_pos[1] = 100  # Move to logbook
        reader2_next_time = elapsed_time_sec() + 0.4
    elif reader2_active and elapsed_time_sec() >= reader2_next_time:
        reader_count -= 1
        if reader_count == 0:
            logbook_locked = False
        show_details(f"Intelligent stuff 2 has finished reviewing logbook at time {elapsed_time_sec():.1f}. Operations completed = {operations_completed}")
        show_details(f"Intelligent stuff 2 is updated status at time {elapsed_time_sec():.1f}")
        reader2_active = False
        reader2_pos[1] = 200  # Move back
        reader2_next_time = elapsed_time_sec() + PERIODICITY * 0.7

async def main():
    global operations_completed
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update operative positions (smooth movement)
        for op in operatives:
            op.pos[0] += (op.target_pos[0] - op.pos[0]) * 0.1
            op.pos[1] += (op.target_pos[1] - op.pos[1]) * 0.1

        # Update operative states
        for op in operatives:
            if op.state == OperativeState.ARRIVING:
                operative_arrival(op)
            elif op.state == OperativeState.WAITING_FOR_RECREATING:
                document_recreation_start(op)
            elif op.state == OperativeState.RECREATING:
                document_recreation_end(op)
            elif op.state == OperativeState.RECREATED and op.is_leader:
                if units[op.unit_id - 1].typewriting_done() and op.state != OperativeState.WAITING_FOR_LOGBOOK:
                    show_details(f"{YELLOW}Unit {op.unit_id} has completed document recreation phase at time {elapsed_time_sec():.1f}")
                    op.state = OperativeState.WAITING_FOR_LOGBOOK
                    logbook_queue.append(op.id)
                    queue_index = list(logbook_queue).index(op.id)
                    op.target_pos = [WIDTH - 150 + LOGBOOK_WIDTH // 2, 100 + LOGBOOK_HEIGHT + (queue_index + 1) * QUEUE_OFFSET]
            elif op.state == OperativeState.WAITING_FOR_LOGBOOK:
                logbook_entry(op)

        # Update readers
        intelligent_stuff_1()
        intelligent_stuff_2()

        # Check for completion
        if operations_completed == num_operatives // unit_size:
            show_details("All operations completed")
            running = False

        # Draw
        screen.fill(BLACK)
        
        # Draw stations
        for station in typewriting_stations:
            color = GREEN if station.state == TypewritingState.FREE else RED
            pygame.draw.rect(screen, color, station.rect)
            text = font.render(f"Station {station.id}", True, WHITE)
            screen.blit(text, (station.rect.x, station.rect.y - 20))
            # Draw queue count
            text = font.render(f"Queue: {len(station.queue)}", True, WHITE)
            screen.blit(text, (station.rect.x, station.rect.y + STATION_HEIGHT + 10))
        
        # Draw operatives
        for op in operatives:
            color = CYAN if op.is_leader else BLUE
            if op.state == OperativeState.RECREATING:
                color = MAGENTA
            elif op.state == OperativeState.LOGBOOK_ENTRY:
                color = YELLOW
            elif op.state == OperativeState.WAITING_FOR_LOGBOOK:
                color = YELLOW
            pygame.draw.circle(screen, color, op.pos, OPERATIVE_RADIUS)
            text = font.render(f"Op {op.id}", True, WHITE)
            screen.blit(text, (op.pos[0] - 10, op.pos[1] - 30))
        
        # Draw logbook
        pygame.draw.rect(screen, WHITE, logbook_rect)
        text = font.render("Logbook", True, BLACK)
        screen.blit(text, (logbook_rect.x + 10, logbook_rect.y + 15))
        # Draw logbook queue count
        text = font.render(f"Logbook Queue: {len(logbook_queue)}", True, WHITE)
        screen.blit(text, (logbook_rect.x, logbook_rect.y + LOGBOOK_HEIGHT + 10))
        
        # Draw readers
        pygame.draw.circle(screen, CYAN, reader1_pos, 10)
        pygame.draw.circle(screen, CYAN, reader2_pos, 10)
        screen.blit(font.render("Reader 1", True, WHITE), (reader1_pos[0] - 20, reader1_pos[1] - 20))
        screen.blit(font.render("Reader 2", True, WHITE), (reader2_pos[0] - 20, reader2_pos[1] - 20))
        
        # Draw log
        pygame.draw.rect(screen, (50, 50, 50), (0, HEIGHT - LOG_HEIGHT, WIDTH, LOG_HEIGHT))
        for i, (msg, _) in enumerate(log_messages):
            text = font.render(msg, True, WHITE)
            screen.blit(text, (10, HEIGHT - LOG_HEIGHT + 10 + i * 20))

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())

pygame.quit()