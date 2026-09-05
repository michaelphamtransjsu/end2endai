# Presentation Narrative — Proving an LLM Can Conduct a Data-Science Experiment

**Recommended length:** 8–10 minutes  
**Format:** Use the seven graphs in `assets/` as the core visual story.

---

## Slide 1 — Title

### On screen
**Can an LLM Do Data Science?**  
NYC Taxi Trip Duration — End-to-End Experiment

### Speaker narrative
For this assignment, I wanted to test more than whether a language model could write Python code. The question was whether an LLM could actually conduct a complete data-science workflow.

I gave it the NYC Taxi Trip Duration dataset and asked it to behave like a senior data scientist. It had to inspect the real uploaded dataset, clean it, perform exploratory analysis, engineer features, train and compare models, evaluate the final model, create visualizations, and explain its conclusions.

I did not run the analytical code locally. The analysis and model experiments were executed by the LLM using its available coding environment.

The final result was a model that reduced average prediction error from a 7.41-minute naive baseline to about 3.10 minutes.

---

## Slide 2 — What Was the Prediction Problem?

### On screen
- 1,458,644 taxi trips
- 11 raw columns
- Target: `trip_duration`
- Regression problem

### Speaker narrative
Each row represented one NYC taxi trip.

The goal was to predict trip duration in seconds using information that could reasonably describe the trip, such as pickup time, passenger count, and pickup and dropoff coordinates.

One important idea throughout the project was to distinguish information that could legitimately be used for prediction from information that would reveal the answer.

That became important immediately during inspection.

---

## Slide 3 — Stage 1 and 2: Inspection and Cleaning

### On screen
**Key findings**
- No missing values
- No duplicate rows
- Extreme duration outliers
- Unusual passenger counts
- Geographic anomalies
- `dropoff_datetime` = target leakage
- Only 0.305% removed

### Speaker narrative
The first thing the LLM did was inspect the actual dataset instead of assuming it matched a standard Kaggle schema.

It found no missing values and no duplicate rows, which was good.

But it also found extreme durations—from one second to more than 40 days—as well as a small number of suspicious passenger counts and coordinates outside the NYC region.

The most important discovery was target leakage.

The LLM verified that subtracting pickup time from dropoff time exactly reproduced trip duration. So if `dropoff_datetime` were included in the model, the model would effectively be given the answer.

The LLM excluded that feature from prediction.

Cleaning was deliberately conservative. Only 4,446 rows were removed out of more than 1.45 million—about 0.305%.

The median trip duration remained about 11 minutes, which suggested the cleaning rules removed anomalies rather than changing the typical trip.

---

## Slide 4 — Stage 3: What Does Trip Duration Look Like?

### Visual
`assets/01_trip_duration_distribution.png`

### Speaker narrative
This graph shows the cleaned trip-duration distribution.

The distribution is strongly right-skewed. Most trips are relatively short, while a smaller number of long trips create the tail.

That mattered later because the LLM tested both the raw duration target and a log-transformed target.

The log transformation reduced target skewness dramatically and ultimately produced the lowest MAE of all the tested models.

The important point is that the modeling decision came from something observed during EDA.

---

## Slide 5 — Stage 3: Distance Was the Strongest Relationship

### Visual
`assets/02_distance_vs_duration.png`

### Speaker narrative
Next, the LLM calculated Haversine distance between pickup and dropoff coordinates.

This graph shows the relationship between straight-line distance and trip duration.

The correlation was approximately 0.77, which is strong.

Median trip duration rose from about 4.5 minutes for trips under one kilometer to more than 45 minutes for trips over 20 kilometers.

This gave us the first major modeling hypothesis:

Distance should be one of the most important predictors.

The LLM then turned that hypothesis into an engineered feature called `distance_km`.

---

## Slide 6 — Stage 3 and 4: Time Matters Too

### Visual
`assets/03_hourly_duration_similar_distance.png`

### Speaker narrative
Distance was not the entire story.

To make the time comparison more meaningful, the LLM looked only at trips between about two and five kilometers.

Even within that relatively similar distance range, trip duration changed dramatically throughout the day.

Trips around 5 AM were much faster than trips during daytime hours.

This suggested that time-of-day conditions contain information beyond distance alone.

The LLM therefore engineered features including pickup hour, weekday, month, weekend status, and rush-hour status.

Again, the feature engineering followed the EDA rather than being arbitrary.

---

## Slide 7 — Stage 5 and 6: Did Machine Learning Actually Help?

### Visual
`assets/04_model_mae_comparison.png`

### Speaker narrative
Before training sophisticated models, the LLM established naive baselines.

The median baseline had a mean absolute error of 7.41 minutes.

Linear Regression improved that to 4.63 minutes.

That showed that the engineered features contained real predictive signal.

But taxi travel is nonlinear. A five-kilometer trip at 5 AM is different from the same distance at 5 PM.

Histogram Gradient Boosting reduced MAE further to 3.10 minutes and achieved an R-squared of about 0.796.

A log-target Gradient Boosting model had the smallest MAE at 3.02 minutes, but slightly worse RMSE and R-squared.

The LLM therefore selected the raw-target Gradient Boosting model as the strongest overall model while reporting the tradeoff honestly.

---

## Slide 8 — Stage 7: Does the Model Generalize?

### Visual
`assets/05_actual_vs_predicted.png`

### Speaker narrative
This graph compares predicted duration with actual duration for unseen test trips.

The test set contained 290,840 trips that were not used to train the model.

If every prediction were perfect, all points would lie on the diagonal line.

The model follows that line reasonably well for the dense region containing ordinary trips.

Its overall MAE was about 3.10 minutes, RMSE was 4.96 minutes, and R-squared was about 0.796.

About 65% of predictions were within three minutes of the true value, and about 83% were within five minutes.

But the graph also shows a weakness: unusually long trips are often underestimated.

That motivated a deeper error analysis.

---

## Slide 9 — Stage 7: Where Does It Fail?

### Visual
`assets/06_error_by_duration_band.png`

### Speaker narrative
This graph is important because it prevents us from hiding behind a single average metric.

For trips under 10 minutes, MAE was around two minutes.

For 30-to-60-minute trips, error rose to almost eight minutes.

For trips between one and three hours, MAE exceeded 19 minutes.

The model tends to overestimate very short trips and underestimate very long trips.

This is a form of regression toward the typical trip.

It also makes sense given the missing information. The dataset does not contain live traffic, accidents, weather, exact road routes, construction, or road closures.

Two trips can look similar in the dataset but have very different real travel times.

---

## Slide 10 — Stage 7: What Did the Model Learn?

### Visual
`assets/07_permutation_feature_importance.png`

### Speaker narrative
Permutation importance allowed the LLM to test which variables the model actually relied on.

Haversine distance was by far the strongest feature.

When distance was shuffled, model MAE deteriorated by roughly 383 seconds, or about 6.4 minutes.

Pickup hour was the second-most-important feature.

Several geographic features and weekday followed.

Passenger count, vendor ID, weekend status, and store-and-forward status added comparatively little.

This completes the reasoning loop.

EDA said distance mattered. Feature engineering created Haversine distance. The trained model later confirmed that distance was its strongest predictor.

EDA showed time-of-day effects. The model later confirmed pickup hour as the second-most-important feature.

That continuity is one of the strongest pieces of evidence that the LLM conducted an actual data-science workflow.

---

## Slide 11 — Did the LLM Do Data Science?

### On screen
**Evidence**
1. Inspected the real dataset
2. Detected leakage
3. Cleaned conservatively
4. Formed hypotheses
5. Engineered evidence-based features
6. Established baselines
7. Compared models
8. Evaluated unseen data
9. Diagnosed failure modes
10. Interpreted feature importance

### Speaker narrative
My conclusion is that the experiment supports the assignment hypothesis.

The LLM did not simply generate a notebook template.

It made decisions that were connected across stages.

It detected and prevented leakage.

It used EDA to identify distance and time as important.

It engineered those variables.

It established baselines before using stronger models.

It selected a model based on multiple metrics rather than a single score.

And it investigated where that model failed.

The final MAE improvement—from 7.41 minutes to 3.10 minutes—is important, but the reasoning trail is stronger evidence than the score itself.

---

## Slide 12 — Limitations and Next Steps

### On screen
**Missing information**
- Traffic
- Weather
- Accidents
- Road closures
- Exact route
- Road-network distance

**Next experiments**
- Time-based validation
- Routing distance
- Traffic/weather features
- XGBoost / LightGBM / CatBoost
- Hyperparameter optimization

### Speaker narrative
The final model is not production-ready.

The most obvious limitation is that it lacks several variables that directly affect travel time.

The next experiment I would prioritize is a time-based split so the model is trained on earlier months and tested on later months. That would better represent deployment.

I would also add actual road-network distance and historical traffic information.

Those additions would test whether the remaining long-trip errors are caused by limitations of the model or limitations of the available data.

---

## Closing

### Speaker narrative
The final takeaway is not that an LLM replaces a data scientist.

The result is that, when given the real dataset and an execution environment, the LLM was able to participate in the complete analytical cycle—from data inspection through model interpretation—and produce a measurable, defensible machine-learning result.

The project reduced mean absolute error by roughly 58% compared with the median baseline while also documenting what the model learned, where it failed, and what should be tested next.

That is the evidence I would use to argue that language models can do more than generate code: they can conduct a structured data-science experiment.
