import tensorflow as tf
import threading
import time


# ============================================================
# SETTINGS
# ============================================================

SIZE = 100
NUM_THREADS = 4


# ============================================================
# CREATE MATRICES AS TENSORS
# ============================================================

print("Creating 100 × 100 tensors...")

A = tf.random.uniform(
    shape=(SIZE, SIZE),
    minval=1,
    maxval=10,
    dtype=tf.float32
)

B = tf.random.uniform(
    shape=(SIZE, SIZE),
    minval=1,
    maxval=10,
    dtype=tf.float32
)

# Result tensor
C = tf.Variable(
    tf.zeros((SIZE, SIZE), dtype=tf.float32)
)


# ============================================================
# THREAD FUNCTION
# ============================================================

def multiply_rows(thread_id, start_row, end_row):

    print(
        f"Thread {thread_id} started "
        f"(rows {start_row} - {end_row - 1})"
    )

    for i in range(start_row, end_row):

        for j in range(SIZE):

            total = 0.0

            for k in range(SIZE):

                total += (
                    A[i, k].numpy()
                    * B[k, j].numpy()
                )

            # Store result
            C[i, j].assign(total)

    print(
        f"Thread {thread_id} finished "
        f"(rows {start_row} - {end_row - 1})"
    )


# ============================================================
# START MULTIPLE THREADS
# ============================================================

threads = []

rows_per_thread = SIZE // NUM_THREADS

start_time = time.time()

for thread_id in range(NUM_THREADS):

    start_row = thread_id * rows_per_thread

    # Last thread gets any remaining rows
    if thread_id == NUM_THREADS - 1:
        end_row = SIZE
    else:
        end_row = start_row + rows_per_thread

    thread = threading.Thread(
        target=multiply_rows,
        args=(thread_id + 1, start_row, end_row)
    )

    threads.append(thread)

    thread.start()


# ============================================================
# WAIT FOR ALL THREADS
# ============================================================

for thread in threads:
    thread.join()


end_time = time.time()


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n======================================")
print("MATRIX MULTIPLICATION COMPLETED")
print("======================================")

print(f"Matrix A shape: {A.shape}")
print(f"Matrix B shape: {B.shape}")
print(f"Result C shape: {C.shape}")

print(f"\nNumber of threads: {NUM_THREADS}")

print(
    f"Execution time: "
    f"{end_time - start_time:.2f} seconds"
)

print("\nFirst 5 × 5 part of Result C:")

print(C[:5, :5].numpy())