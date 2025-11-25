#include<bits/stdc++.h>
#include <semaphore.h>
using namespace std;

#define LAMBDA 10000.234
#define NUM_STATIONS 4
#define MAX_ARRIVAL_DELAY 8
#define SLEEP_MUTIPLE 1000000
#define PERIODICITY 3

string RESET   = "\033[0m";
string RED     = "\033[31m";
string GREEN   = "\033[32m";
string YELLOW  = "\033[33m";
string BLUE    = "\033[34m";
string MAGENTA = "\033[35m";
string CYAN    = "\033[36m";
string WHITE   = "\033[37m"; 

string BG_BLACK      = "\033[40m";
string BG_RED        = "\033[41m";
string BG_GREEN      = "\033[42m";
string BG_YELLOW     = "\033[43m";
string BG_BLUE       = "\033[44m";
string BG_MAGENTA    = "\033[45m";
string BG_CYAN       = "\033[46m";
string BG_WHITE      = "\033[47m";



int num_operatives;
int unit_size;
int document_recreation_interval;
int logbook_entry_interval ;
int operations_completed = 0;
int reader_count = 0;


pthread_mutex_t cout_mutex;
pthread_mutex_t count_mutex;
pthread_mutex_t notify_mutex;
pthread_mutex_t logbook_mutex;
pthread_mutex_t reader_count_mutex;
vector<pthread_mutex_t> mutex_recreating;

auto begin_time=std::chrono::high_resolution_clock::now();

auto elapsed_time_ms() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(
      std::chrono::high_resolution_clock::now() - begin_time).count();
}

auto elapsed_time_sec() {
   return std::chrono::duration_cast<std::chrono::seconds>(
      std::chrono::high_resolution_clock::now() - begin_time).count();
}

int get_random_number(double lambda = LAMBDA) {
  std::random_device rd;
  std::mt19937 generator(rd());
  std::poisson_distribution<int> poissonDist(lambda);
  return poissonDist(generator);
}

// int get_random_number(int min=1, int max=10) {
//   std::random_device rd;
//   std::mt19937 generator(rd());
//   std::uniform_int_distribution<int> uniformDist(min, max);
//   return uniformDist(generator);
// }

enum typewriting_state {
  FREE,
  OCCUPIED
};

class Typewriting_station {
public:
  int id;
  typewriting_state state;

  Typewriting_station(int id) {
    this->id = id;
    this->state = FREE;
  }
};

enum operative_state {
  ARRIVING,
  WAITING_FOR_RECREATING,
  RECREATING,
  RECREATED,
  LOGBOOK_ENTRY
};

int station_assignment_protocol(int operative_id) {
  return operative_id % NUM_STATIONS + 1;
}

int arrival_delay_protocol() {
  return get_random_number() % MAX_ARRIVAL_DELAY + 1;
}

int unit_assignment_protocol(int operative_id) {
  return (operative_id - 1) / unit_size + 1;
}

bool leader_assignment_protocol(int operative_id) {
  return operative_id % unit_size == 0;
}

class Operative {
public:
  int id;
  int unit_id;
  int typewriting_station_id;
  operative_state state;
  int arrival_delay;
  bool is_leader;
  int arrival_time;

  Operative(int id) {
    this->id = id;
    this->unit_id = unit_assignment_protocol(id);
    this->typewriting_station_id = station_assignment_protocol(id);
    this->state = ARRIVING;
    this->arrival_delay = arrival_delay_protocol();
    this->is_leader = leader_assignment_protocol(id);
    
  }
};


class Unit{
public:
  int id;
  int leader_id;
  int typewriting_completion_count;
  sem_t completion;

  Unit(int id) {
    this->id = id;
    this->leader_id = (this->id) * unit_size;
    this->typewriting_completion_count = 0;
    sem_init(&completion, 0, 0);
  }
  bool typewriting_done() {
    return this->typewriting_completion_count == unit_size;
  }
  void increment_typewriting_completion_count() {
    this->typewriting_completion_count++;
  }
};




vector<Typewriting_station> typewriting_station;
vector<Unit> units;
vector<Operative> operatives;
pthread_mutex_t typewriting_station_mutex[NUM_STATIONS];




void show_details(string details)
{
  pthread_mutex_lock(&cout_mutex);
  cout << details << endl <<endl;
  pthread_mutex_unlock(&cout_mutex);
}

void notify_document_recreation_end(int operative_id) {

  vector<int> waiting_operatives;
  for(auto operative : operatives) {
    if(operative.state == WAITING_FOR_RECREATING && operative.typewriting_station_id == operatives[operative_id - 1].typewriting_station_id) {
      waiting_operatives.push_back(operative.id);
    }
  }
  sort(waiting_operatives.begin(), waiting_operatives.end(), [](int a, int b) {
    return operatives[a - 1].arrival_time < operatives[b - 1].arrival_time;
  });
  string waiters_str = "";
  for(auto waiter : waiting_operatives) {
    waiters_str += to_string(waiter) + " ";

  }
  show_details(GREEN+"Operative " + to_string(operative_id) + " has notified document recreation end at time " + to_string(elapsed_time_sec()) + ". Waiting operatives: " + waiters_str + RESET);
}
void operative_arrival(int id) {
  int operative_id = id;
  int unit_id = operatives[operative_id - 1].unit_id;
  int typewriting_station_id = operatives[operative_id - 1].typewriting_station_id;
 
  usleep(operatives[operative_id - 1].arrival_delay * SLEEP_MUTIPLE); 
  int arrival_time = elapsed_time_sec();
  show_details("Operative " + to_string(operative_id) + " [from unit " + to_string(unit_id) + "] has arrived at typewriting station " + to_string(typewriting_station_id) + " at time " + to_string(arrival_time));
  operatives[operative_id - 1].arrival_time = arrival_time;
   operatives[operative_id-1].state = WAITING_FOR_RECREATING;
}

void document_recreation_start(int id) {
  int operative_id = id;
  int unit_id = operatives[operative_id - 1].unit_id;
  int typewriting_station_id = operatives[operative_id - 1].typewriting_station_id;
  typewriting_station[typewriting_station_id-1].state=OCCUPIED;
  operatives[operative_id-1].state = RECREATING;
  usleep(document_recreation_interval * SLEEP_MUTIPLE);
}


void document_recreation_end(int id) {
  int operative_id = id;
  int unit_id = operatives[operative_id - 1].unit_id;
  int typewriting_station_id = operatives[operative_id - 1].typewriting_station_id;
  
  operatives[operative_id - 1].state = RECREATED;

 


  
  pthread_mutex_lock(&notify_mutex);
  show_details(GREEN+"Operative " + to_string(operative_id) + " [from unit " + to_string(unit_id) + 
               "] has completed document recreation at typewriting station " + 
               to_string(typewriting_station_id) + " at time " + to_string(elapsed_time_sec()) + RESET);
  notify_document_recreation_end(operative_id);
  pthread_mutex_unlock(&notify_mutex);

  pthread_mutex_lock(&mutex_recreating[unit_id - 1]);
  sem_post(&units[unit_id - 1].completion);
  units[unit_id - 1].increment_typewriting_completion_count();
  pthread_mutex_unlock(&mutex_recreating[unit_id - 1]);

    show_details(RED+"Operative " + to_string(operative_id) + " [from unit " + to_string(unit_id) + 
               "] handled over document " + 
               to_string(units[unit_id - 1].typewriting_completion_count) + 
               " to the leader of unit " + to_string(unit_id) + " at time " + to_string(elapsed_time_sec()) + RESET);





}


void logbook_entry(int operative_id) {
  int unit_id = operatives[operative_id - 1].unit_id;
  operatives[operative_id - 1].state = LOGBOOK_ENTRY;

  pthread_mutex_lock(&logbook_mutex);
  show_details(BLUE+"Unit " + to_string(unit_id) + " has started intelligence distribution at time " + to_string(elapsed_time_sec()) + RESET);
  usleep(logbook_entry_interval * SLEEP_MUTIPLE);
  show_details(BLUE+"Unit " + to_string(unit_id) + " has completed intelligence distribution at time " + to_string(elapsed_time_sec()) + RESET);
  operations_completed++;
  pthread_mutex_unlock(&logbook_mutex);
 
}

void *operative_thread_funtion(void *arg) {
  Operative *operative = (Operative *)arg;
  int operative_id = operative->id;
  int unit_id = operative->unit_id;
  int typewriting_station_id = operative->typewriting_station_id;
  int arrival_delay = operative->arrival_delay;

  operative_arrival(operative_id);

  pthread_mutex_lock(&typewriting_station_mutex[typewriting_station_id - 1]);
  document_recreation_start(operative_id);
  document_recreation_end(operative_id);
  pthread_mutex_unlock(&typewriting_station_mutex[typewriting_station_id - 1]);
  typewriting_station[typewriting_station_id - 1].state = FREE;


    if(operatives[operative_id - 1].is_leader) {
    for(int i=1;i<=unit_size;i++) {

      sem_wait(&units[unit_id - 1].completion);
  
    }

    if(units[unit_id - 1].typewriting_done()) {
      show_details(  YELLOW+  "Unit " + to_string(unit_id) + " has completed document recreation phase at time " + to_string(elapsed_time_sec()) + RESET);
    }

    logbook_entry(operative_id);
  }
  
  return NULL;
}



void *intelligent_stuff_1(void *arg) {
     usleep((get_random_number()%MAX_ARRIVAL_DELAY) * SLEEP_MUTIPLE); 
    while(1){
    pthread_mutex_lock(&reader_count_mutex);
    reader_count++;
    if (reader_count == 1) pthread_mutex_lock(&logbook_mutex);
    show_details(BG_RED+ "Intelligent stuff 1 has began reviewing logbook at time " + to_string(elapsed_time_sec()) + ". Operations completed = " + to_string(operations_completed)+RESET);
    pthread_mutex_unlock(&reader_count_mutex);


    usleep(2 * SLEEP_MUTIPLE);

    pthread_mutex_lock(&reader_count_mutex);
    reader_count--;
    if (reader_count == 0) pthread_mutex_unlock(&logbook_mutex);
    show_details(BG_RED+ "Intelligent stuff 1 has finished reviewing logbook at time " + to_string(elapsed_time_sec()) + ". Operations completed = " + to_string(operations_completed)+RESET);
    show_details(BG_RED+ "Intelligent stuff 1 is calling Shelby bhai at time " + to_string(elapsed_time_sec()) + RESET);
    pthread_mutex_unlock(&reader_count_mutex);

    usleep(PERIODICITY * SLEEP_MUTIPLE); 

    if(operations_completed == num_operatives / unit_size) {
      
      return NULL;
     
    }
  }
 return NULL; 
}


void *intelligent_stuff_2(void *arg) {
    usleep((get_random_number()%MAX_ARRIVAL_DELAY) * SLEEP_MUTIPLE); 

    while(1){
    pthread_mutex_lock(&reader_count_mutex);
    reader_count++;
    if (reader_count == 1) pthread_mutex_lock(&logbook_mutex);
    show_details(BG_GREEN+"Intelligent stuff 2 has began reviewing logbook at time " + to_string(elapsed_time_sec()) + ". Operations completed = " + to_string(operations_completed)+RESET);
    pthread_mutex_unlock(&reader_count_mutex);


    usleep(1 * SLEEP_MUTIPLE);

    pthread_mutex_lock(&reader_count_mutex);
    reader_count--;
    if (reader_count == 0) pthread_mutex_unlock(&logbook_mutex);
    show_details(BG_GREEN+"Intelligent stuff 2 has finished reviewing logbook at time " + to_string(elapsed_time_sec()) + ". Operations completed = " + to_string(operations_completed)+RESET);
    show_details(BG_GREEN+"Intelligent stuff 2 is updated status at time " + to_string(elapsed_time_sec())+RESET);
    pthread_mutex_unlock(&reader_count_mutex);

    usleep(PERIODICITY * 1.5 * SLEEP_MUTIPLE);

    if(operations_completed == num_operatives / unit_size) {
      
      return NULL;
     
    }
  }
 return NULL; 
}


void init()
{
  
  pthread_mutex_init(&cout_mutex, NULL);
  pthread_mutex_init(&count_mutex, NULL);
  pthread_mutex_init(&notify_mutex, NULL);
  pthread_mutex_init(&logbook_mutex, NULL);
  pthread_mutex_init(&reader_count_mutex, NULL);

  for (int i = 0; i < NUM_STATIONS; i++) {
    pthread_mutex_init(&typewriting_station_mutex[i], NULL);
  }

  for (int i = 1; i <= NUM_STATIONS; i++) {
    typewriting_station.emplace_back(Typewriting_station(i));
  }

  for (int i = 1; i <= num_operatives; i++) {
    operatives.emplace_back(Operative(i));
  }

  for (int i = 1; i <= num_operatives / unit_size; i++) {
    units.emplace_back(Unit(i));
  }

   mutex_recreating.resize(num_operatives / unit_size);

  for(int i=0;i<num_operatives / unit_size;i++) {
    pthread_mutex_init(&mutex_recreating[i], NULL);
  }
}

int main(int argc, char *argv[]) {
  if (argc != 3) {
    std::cout << "Usage: ./a.out <input_file> <output_file>" << std::endl;
    return 0;
  }

  // File handling for input and output redirection  //copied from student_report_printing.cpp
  std::ifstream inputFile(argv[1]);
  std::streambuf *cinBuffer = std::cin.rdbuf(); // Save original std::cin buffer
  std::cin.rdbuf(inputFile.rdbuf()); // Redirect std::cin to input file

  // std::ofstream outputFile(argv[2]);
  // std::streambuf *coutBuffer = std::cout.rdbuf(); // Save original cout buffer
  // std::cout.rdbuf(outputFile.rdbuf()); // Redirect cout to output file

  int N, M, x, y;
  cin >> N >> M >> x >> y;
  
  num_operatives = N;
  unit_size = M;
  document_recreation_interval = x;
  logbook_entry_interval = y;


  init();
  pthread_t operative_threads[num_operatives];

  pthread_t intelligent_stuff_1_thread, intelligent_stuff_2_thread;
  pthread_create(&intelligent_stuff_1_thread, NULL, intelligent_stuff_1, NULL);
  pthread_create(&intelligent_stuff_2_thread, NULL, intelligent_stuff_2, NULL);

  for(int i = 0; i < num_operatives; i++) {
    pthread_create(&operative_threads[i], NULL, operative_thread_funtion , &operatives[i]);
  }

  for(int i = 0; i < num_operatives; i++) {
    pthread_join(operative_threads[i], NULL);
  }


  pthread_join(intelligent_stuff_1_thread, NULL);
  pthread_join(intelligent_stuff_2_thread, NULL);

  show_details("All operations completed");

  pthread_mutex_destroy(&cout_mutex);
  pthread_mutex_destroy(&count_mutex);
  pthread_mutex_destroy(&notify_mutex);
  pthread_mutex_destroy(&logbook_mutex);
  pthread_mutex_destroy(&reader_count_mutex);


  for (int i = 0; i < NUM_STATIONS; i++) {
    pthread_mutex_destroy(&typewriting_station_mutex[i]);
  }

  for(int i=0;i<num_operatives / unit_size;i++) {
    pthread_mutex_destroy(&mutex_recreating[i]);
  }

  for (int i = 0; i < num_operatives / unit_size; i++) {
    sem_destroy(&units[i].completion);
  }


  return 0;
}