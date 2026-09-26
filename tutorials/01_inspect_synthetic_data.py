"""Tutorial 01: inspect a small, explicitly synthetic DAS-like array.

Run from the repository root after installation:

    python tutorials/01_inspect_synthetic_data.py
"""

from das_student_lab import format_summary, make_synthetic_whale, summarize_array


def main() -> None:
    print(
        "Before diving in, here's what's actually happening physically. DAS "
        "works by sending laser pulses down a standard fiber optic cable. The "
        "glass isn't perfectly uniform, so tiny imperfections scatter a small "
        "amount of light backward, called Rayleigh backscatter. That pattern "
        "is normally stable, but if the cable stretches or compresses even "
        "slightly, from sound, vibration, or ground motion nearby, it changes "
        "the returning light's timing and phase at that exact point in the "
        "fiber. By measuring how that backscatter changes over time, the "
        "system detects strain at thousands of points along the cable at "
        "once.\n\n"
        "Each of those points is a 'channel'. They aren't separate physical "
        "sensors, they're just measurement points along one continuous fiber, ")
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
    print("\nSoftware: das_student_lab (this project), NumPy")
    print("Note: this tutorial uses only synthetic data, no external dataset citation applies.")
    print("\nQuestions to answer in your own words:")
    print("1. Which axis represents channels, and which represents time?")
    print("2. Why is distance span (channels - 1) x spacing?")
    print("3. Which properties were declared by the caller rather than inferred?")
    print("4. Why must this synthetic signal not be described as measured whale data?")


if __name__ == "__main__":
    main()
