
import requests
import math

BASE_URL = "http://localhost:8000"

# Five sensor fields used by the neural network
VALID_READING = {
    "battery_v": 3.0,
    "temp_c": 25.0,
    "rings_per_day": 20,
    "wifi_rssi_dbm": -60,
    "age_months": 6
}

def check(name, condition, details=""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name} {details}")


def main():
    print("\n========== API EDGE-CASE TESTS ==========\n")

    # 1. Test all five invalid sensor readings
    invalid_cases = [
        ("Battery voltage too low", {"battery_v": -1}),
        ("Temperature too high", {"temp_c": 100}),
        ("Rings per day too high", {"rings_per_day": 1001}),
        ("WiFi signal too low", {"wifi_rssi_dbm": -110}),
        ("Age too high", {"age_months": 121}),
    ]

    for name, invalid_field in invalid_cases:
        reading = VALID_READING.copy()
        reading.update(invalid_field)
        response = requests.post(BASE_URL + "/predict", json=reading)
        check(name, response.status_code == 422,
              f"(HTTP {response.status_code})")

    # 2. Test minimum and maximum allowed values
    minimum = {
        "battery_v": 0,
        "temp_c": -40,
        "rings_per_day": 0,
        "wifi_rssi_dbm": -100,
        "age_months": 0
    }

    maximum = {
        "battery_v": 5,
        "temp_c": 85,
        "rings_per_day": 1000,
        "wifi_rssi_dbm": 0,
        "age_months": 120
    }

    for name, reading in [
        ("All minimum boundaries", minimum),
        ("All maximum boundaries", maximum)
    ]:
        response = requests.post(BASE_URL + "/predict", json=reading)
        valid = False
        if response.status_code == 200:
            result = response.json()
            valid = (
                isinstance(result.get("days_left"), (int, float))
                and math.isfinite(result["days_left"])
                and result["days_left"] >= 0
            )
        check(name, valid, f"(HTTP {response.status_code})")

    # 3. Test missing field
    incomplete = VALID_READING.copy()
    del incomplete["battery_v"]
    response = requests.post(BASE_URL + "/predict", json=incomplete)
    check("Missing required field",
          response.status_code == 422,
          f"(HTTP {response.status_code})")

    # 4. Test incorrect data type
    wrong_type = VALID_READING.copy()
    wrong_type["battery_v"] = "not-a-number"
    response = requests.post(BASE_URL + "/predict", json=wrong_type)
    check("Incorrect sensor data type",
          response.status_code == 422,
          f"(HTTP {response.status_code})")


    # 5. Generate 50 different valid readings
    readings = []
    for i in range(50):
        readings.append({
            "battery_v": round(3.4 + (i % 8) * 0.1, 2),
            "temp_c": 15 + (i % 25),
            "rings_per_day": i % 30,
            "wifi_rssi_dbm": -85 + (i % 40),
            "age_months": i % 37
        })

    # 6. Send all 50 readings in ONE batch request
    batch_response = requests.post(
        BASE_URL + "/predict_batch",
        json={"rows": readings}
    )

    batch_ok = batch_response.status_code == 200
    batch_predictions = []

    if batch_ok:
        batch_result = batch_response.json()
        batch_predictions = batch_result.get("days_left", [])

        batch_ok = (
            len(batch_predictions) == 50
            and all(
                isinstance(v, (int, float))
                and math.isfinite(v)
                and v >= 0
                for v in batch_predictions
            )
        )

    check("50-reading batch", batch_ok,
          f"(HTTP {batch_response.status_code})")

    # 7. Check all five timing fields
    timing_fields = {
        "parse", "normalise", "inference", "build", "server_total"
    }

    timing_ok = False
    if batch_response.status_code == 200:
        timings = batch_response.json().get("timings_ms", {})
        timing_ok = (
            timing_fields.issubset(timings)
            and all(
                isinstance(timings[k], (int, float))
                and math.isfinite(timings[k])
                and timings[k] >= 0
                for k in timing_fields
            )
        )

    check("All five batch timing fields", timing_ok)

    # 8. Send the same 50 readings individually
    individual_predictions = []
    individual_ok = True

    for reading in readings:
        response = requests.post(
            BASE_URL + "/predict",
            json=reading
        )

        if response.status_code != 200:
            individual_ok = False
            break

        result = response.json()
        value = result.get("days_left")

        if not isinstance(value, (int, float)) or not math.isfinite(value):
            individual_ok = False
            break

        individual_predictions.append(value)

    check("50 individual predictions", individual_ok)

    # 9. Compare batch and individual predictions
    consistency = (
        batch_ok
        and individual_ok
        and len(individual_predictions) == 50
        and all(
            abs(a - b) <= 0.01
            for a, b in zip(batch_predictions, individual_predictions)
        )
    )

    check("Batch matches individual predictions", consistency)

    # 10. Empty batch must be rejected
    empty_response = requests.post(
        BASE_URL + "/predict_batch",
        json={"rows": []}
    )

    check("Empty batch rejected",
          empty_response.status_code == 422)

    print("\n========== BATCH TESTS COMPLETE ==========\n")

if __name__ == "__main__":
    main()
