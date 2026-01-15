from muffin.utils import fraction_to_float


def test_fraction_to_float():
    test_cases = {
        "1/2": 0.5,
        "3/4": 0.75,
        "2": 2.0,
        "5.5": 5.5,
        "7,25": 7.25,
    }

    for input_str, expected in test_cases.items():
        result = fraction_to_float(input_str)
        assert result == expected, f"Failed for input: {input_str}"
