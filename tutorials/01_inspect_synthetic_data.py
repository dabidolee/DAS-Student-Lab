"""Tutorial 01: inspect a small, explicitly synthetic DAS-like array.

Run from the repository root after installation:

    python tutorials/01_inspect_synthetic_data.py
"""

from das_student_lab import format_summary, make_synthetic_whale, summarize_array


def main() -> None:
    print("Learning goal: connect array shape to time, distance, and memory.\n")
    print(
        "Prediction: if the sample rate doubles but duration stays fixed, "
        "what changes?\n"
    )

    example = make_synthetic_whale(seed=7)
    print(example.description)
    print()

    summary = summarize_array(
        example.data,
        sample_rate_hz=example.sample_rate_hz,
        channel_spacing_m=example.channel_spacing_m,
    )
    print(format_summary(summary))

    print("\nQuestions to answer in your own words:")
    print("1. Which axis represents channels, and which represents time?")
    print("2. Why is distance span (channels - 1) x spacing?")
    print("3. Which properties were declared by the caller rather than inferred?")
    print("4. Why must this synthetic signal not be described as measured whale data?")


if __name__ == "__main__":
    main()
