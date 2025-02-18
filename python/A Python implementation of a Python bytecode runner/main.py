from interpreter import VM
import example


if __name__ == "__main__":
    func = example
    val = VM.call_func(example.example_func, [2, 3], vars(example))
    print(f"Last Val '{val}'")
