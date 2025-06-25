def run_simulator(input_data, steps=10):
    state = input_data.copy()
    for i in range(steps):
        state["step"] = i + 1
        state["status"] = "Running"
    state["status"] = "Complete"
    return state
