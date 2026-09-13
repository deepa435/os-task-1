package tasks;

import java.util.LinkedList;
import java.util.Queue;

public class ProducerConsumer {

    static class Buffer {

        Queue<Integer> items = new LinkedList<>();
        int capacity = 5;

        void add(int item) {
            if (items.size() < capacity) {
                items.add(item);

                System.out.println("Produced: " + item);
                System.out.println("Buffer: " + items);
            }
        }

        void remove() {
            if (!items.isEmpty()) {
                int item = items.remove();

                System.out.println("Consumed: " + item);
                System.out.println("Buffer: " + items);
            }
        }
    }

    static class Producer extends Thread {

        Buffer buffer;

        Producer(Buffer buffer) {
            this.buffer = buffer;
        }

        public void run() {

            for (int i = 1; i <= 10; i++) {

                buffer.add(i);

                try {
                    Thread.sleep(500);
                } catch (Exception e) {
                    System.out.println(e);
                }
            }

            System.out.println("Producer finished.");
        }
    }

    static class Consumer extends Thread {

        Buffer buffer;

        Consumer(Buffer buffer) {
            this.buffer = buffer;
        }

        public void run() {

            for (int i = 1; i <= 10; i++) {

                buffer.remove();

                try {
                    Thread.sleep(800);
                } catch (Exception e) {
                    System.out.println(e);
                }
            }

            System.out.println("Consumer finished.");
        }
    }

    public static void main(String[] args) {

        Buffer buffer = new Buffer();

        Producer pr = new Producer(buffer);
        Consumer cr = new Consumer(buffer);

        pr.start();
        cr.start();
    }
}

