# Model Card: NYC Taxi Duration MVP

## Model details

Version 0.1.0 is a scikit-learn histogram gradient boosting regressor wrapped in a serializable feature pipeline. It is trained locally with a fixed random seed. The repository's artifact is fitted only on the bundled synthetic sample.

## Intended use

Educational demonstrations, local API integration, and a starting point for experiments. Not intended for fare setting, driver evaluation, route choice, safety decisions, accessibility commitments, or production arrival guarantees.

## Inputs and output

Inputs are pickup timestamp, pickup/dropoff latitude and longitude, and passenger count. Output is an estimated duration in seconds (and API convenience conversion to minutes). Coordinates must fall within broad NYC bounds.

## Training and evaluation

Training uses the earliest 80% of time-ordered sample rows; evaluation uses the latest 20%. The baseline is the training median. Metrics are MAE seconds and RMSLE, recorded by training in `artifacts/metrics.json`. No test rows are used for fitting or tuning.

## Limitations and ethics

Synthetic data is structurally simple and is not representative of taxi populations, boroughs, congestion, weather, road closures, mobility needs, or rare events. Coordinate bounds do not prove a point is drivable. Errors could be geographically and temporally unequal. Do not treat apparent sample accuracy as external validity. Joblib artifacts must only be loaded from trusted sources because deserialization can execute code.

## Monitoring

For real data, monitor schema/range failures, distance and time distributions, MAE/RMSLE over time, subgroup residuals by borough and hour, tail errors, and API latency. Establish review thresholds, version data/code/artifacts, and roll back on drift or regressions.
