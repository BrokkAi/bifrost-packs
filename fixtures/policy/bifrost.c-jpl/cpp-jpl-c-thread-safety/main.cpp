void sleep(int);
void task_delay(int);
void wait_for_event();

void synchronize_badly() {
    sleep(1);
    task_delay(1);
}

void synchronize_well() {
    wait_for_event();
}

void unrelated_sleep_name() {
    // The callee name is deliberately different from the exact forbidden names.
    my_sleep(1);
}
