import pandas as pd
import pytest
from taxi_duration.features import engineer_features, validate_frame

def row(): return {"pickup_datetime":"2016-01-01T08:00:00","pickup_latitude":40.75,"pickup_longitude":-73.99,"dropoff_latitude":40.76,"dropoff_longitude":-73.97,"passenger_count":1}
def test_features_are_geographic_and_temporal():
    got=engineer_features(pd.DataFrame([row()]))
    assert got.distance_km.iloc[0] > 1
    assert got.hour.iloc[0] == 8 and got.is_rush_hour.iloc[0] == 1

def test_validation_rejects_bad_coordinate():
    value=row(); value["pickup_latitude"]=0
    with pytest.raises(ValueError, match="bounds"): validate_frame(pd.DataFrame([value]))
