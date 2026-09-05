# I Let an LLM Run an Entire NYC Taxi Data-Science Project. Here’s What Happened.

## From 1.46 million raw taxi trips to a model with roughly 3-minute average error

Most demonstrations of AI in data science stop at code generation.

Ask a language model for a Pandas snippet. Ask it to write a regression model. Ask it to explain a chart.

That is useful, but it does not answer the more interesting question:

> **Can a language model actually conduct the full data-science process?**

For this experiment, I gave an LLM the NYC Taxi Trip Duration dataset and treated it like the data scientist responsible for the project.

The model had to inspect the real data, identify problems, clean it, explore relationships, engineer features, train multiple models, evaluate them on unseen trips, generate visualizations, interpret the final model, and explain its limitations.

The result was a complete machine-learning workflow that reduced mean absolute prediction error from a naive **7.41 minutes** to about **3.10 minutes**.

This article walks through what the LLM did—and, more importantly, the reasoning that connected each stage.

---

## The problem

The task was straightforward to state:

> Given information about an NYC taxi trip, predict how long the trip will take.

The target variable was `trip_duration`, measured in seconds.

The dataset contained **1,458,644 trips and 11 columns**, including pickup and dropoff timestamps, pickup and dropoff coordinates, passenger count, vendor information, and the trip duration.

The project was a regression problem because the target was continuous.

But before training a model, the LLM had to determine whether the data could be trusted.

---

## Stage 1: The first important discovery was not a model

The dataset was surprisingly complete:

- no missing values,
- no exact duplicate rows,
- no duplicate trip IDs.

That sounds like good news—and it was.

But inspection also uncovered several suspicious values.

The shortest trip was only one second. The longest was approximately 40.8 days. Passenger counts ranged from zero to nine. A small number of geographic coordinates were far outside NYC.

Then came the most important finding in the entire inspection stage.

The LLM verified that:

`dropoff_datetime - pickup_datetime = trip_duration`

for every record.

That meant `dropoff_datetime` could not be used as a predictor.

If a model knows when a trip starts and when it ends, it already knows the duration. Including that variable would create **target leakage** and produce misleadingly strong performance.

The first major data-science contribution of the LLM was therefore not an algorithm.

It was recognizing what **not** to feed the algorithm.

---

## Stage 2: Cleaning only what could be defended

Instead of deleting every statistical outlier, the LLM used conservative domain-oriented rules.

Trips were retained if they:

- lasted more than 10 seconds,
- lasted no more than 3 hours,
- had between one and six passengers,
- and had pickup and dropoff coordinates inside a broad NYC/nearby geographic region.

Only **4,446 rows** were removed.

That was approximately **0.305%** of the original dataset.

After cleaning, **1,454,198 trips remained**.

An important sanity check was that the median trip duration stayed at approximately **11 minutes**. Cleaning removed extreme anomalies without substantially changing what a normal trip looked like.

---

## Stage 3: EDA turned raw columns into hypotheses

The trip-duration distribution was strongly right-skewed.

![Trip-duration distribution](assets/01_trip_duration_distribution.png)

Most trips were short or medium length, with a long tail of less-common long trips.

A log transformation reduced target skewness dramatically, which later motivated an alternative model trained on log duration.

But the most important EDA question was:

> What appears to explain trip duration?

### Distance immediately stood out

The LLM calculated Haversine distance between the pickup and dropoff coordinates.

![Distance vs trip duration](assets/02_distance_vs_duration.png)

The correlation between distance and trip duration was approximately **0.77**.

Median trip duration also rose consistently with distance. Trips under one kilometer had median duration around 4.5 minutes, while trips over 20 kilometers had median duration above 45 minutes.

That made distance an obvious feature-engineering candidate.

### But distance was not enough

The next analysis restricted attention to trips between roughly 2 and 5 kilometers.

If distance were the entire story, their durations should have been relatively stable throughout the day.

They were not.

![Time-of-day effect](assets/03_hourly_duration_similar_distance.png)

Early-morning trips were much faster than daytime trips of similar distance.

That suggested time-of-day conditions—most plausibly traffic-related effects—contained predictive information beyond distance.

EDA had now produced two strong hypotheses:

1. **How far the taxi travels matters.**
2. **When the taxi travels matters.**

---

## Stage 4: Feature engineering followed the evidence

The LLM converted those hypotheses into model inputs.

Engineered features included:

- Haversine distance,
- pickup hour,
- weekday,
- month,
- weekend indicator,
- rush-hour indicator,
- latitude displacement,
- longitude displacement,
- and a simplified Manhattan-coordinate distance.

The raw pickup and dropoff coordinates were retained too.

The trip ID was excluded because it contained no meaningful travel information.

`dropoff_datetime` was excluded because it leaked the target.

This is what good feature engineering should look like: not generating dozens of arbitrary columns, but translating observed relationships into variables a model can use.

---

## Stage 5: Start with something intentionally bad

Before training powerful models, the LLM created dummy baselines.

The median baseline essentially said:

> Every trip will take about the typical trip duration.

Its mean absolute error was **7.41 minutes**.

That number gave every later model something concrete to beat.

Linear Regression reduced MAE to **4.63 minutes**.

That alone proved the engineered variables contained real predictive information.

But NYC taxi duration is not a purely linear problem.

A five-kilometer trip at 5 AM is not equivalent to a five-kilometer trip at 5 PM.

That motivated nonlinear models.

---

## Stage 6: Nonlinear models captured more of the real structure

The model comparison looked like this:

![Model comparison](assets/04_model_mae_comparison.png)

The verified results were:

| Model | MAE | RMSE | R² |
|---|---:|---:|---:|
| Median baseline | 7.41 min | 11.37 min | -0.072 |
| Mean baseline | 7.80 min | 10.98 min | ~0.000 |
| Linear Regression | 4.63 min | 6.83 min | 0.613 |
| Histogram Gradient Boosting | **3.10 min** | **4.96 min** | **0.796** |
| Log-target Gradient Boosting | **3.02 min** | 5.08 min | 0.787 |

The raw-target Histogram Gradient Boosting model was selected as the best overall model because it had the strongest combination of RMSE and R².

The log-target model had the lowest MAE.

That tradeoff was useful. It showed that “best” depends on what type of error matters.

The log model did slightly better on typical absolute error, while the raw model handled larger mistakes somewhat better.

---

## Stage 7: A single score was not enough

A model with MAE around three minutes sounds good.

But where does it fail?

The held-out test set contained **290,840 unseen trips**.

The raw Gradient Boosting model achieved:

- **MAE:** 3.10 minutes
- **RMSE:** 4.96 minutes
- **R²:** 0.796
- approximately **65%** of predictions within 3 minutes,
- approximately **83%** within 5 minutes,
- and almost **96%** within 10 minutes.

The actual-vs-predicted graph showed that the model tracked ordinary trips reasonably well.

![Actual vs predicted](assets/05_actual_vs_predicted.png)

The weakness became obvious as trips became longer.

![Error by trip length](assets/06_error_by_duration_band.png)

For trips under 10 minutes, MAE was around two minutes.

For trips between 30 and 60 minutes, MAE rose to almost eight minutes.

For 60–180 minute trips, it exceeded 19 minutes.

The model also displayed a recognizable statistical behavior: **regression toward the typical trip**.

It tended to overestimate very short trips and underestimate very long ones.

That limitation would have been invisible if the project stopped at a single overall MAE score.

---

## What actually drove the predictions?

Permutation importance provided one of the clearest results in the entire project.

![Feature importance](assets/07_permutation_feature_importance.png)

Haversine distance dominated.

When that feature was shuffled, MAE worsened by roughly **383 seconds**, or about **6.4 minutes**.

Pickup hour was the second-most-important feature.

Several geographic and weekday variables followed.

Passenger count, vendor ID, weekend status, and store-and-forward status contributed comparatively little once the stronger spatial and temporal features were known.

This was especially satisfying because it completed the reasoning loop:

**EDA discovered the distance relationship → feature engineering created Haversine distance → model interpretation confirmed that Haversine distance was the model's strongest input.**

The same happened for time of day.

That is what made the experiment feel like genuine data science rather than code generation.

---

## Did Haversine beat “Manhattan distance”?

One question that came up during the project was whether a Manhattan-style distance would be better for New York City.

The simplified Manhattan-coordinate feature used in the experiment was:

`abs(latitude difference) + abs(longitude difference)`

It was not actual road-network Manhattan distance.

Permutation importance showed:

- Haversine distance: roughly **383 seconds** of MAE impact when shuffled
- simplified Manhattan-coordinate distance: roughly **1 second**

So Haversine was dramatically more useful in this model.

That does **not** mean actual street-network driving distance would be worse than Haversine. In fact, real road distance could be stronger.

It only shows that the simple coordinate approximation added almost nothing once Haversine distance and the geographic coordinates were already present.

---

## What the model still does not know

Even the best model is missing several variables that matter in the real world:

- live traffic,
- weather,
- accidents,
- construction,
- road closures,
- the exact route driven,
- actual road distance,
- traffic lights,
- driver behavior.

Two trips can have the same pickup, destination, hour, weekday, and straight-line distance while experiencing very different travel conditions.

No algorithm can recover information that is not represented in its inputs.

That helps explain why long or unusual trips remained difficult.

---

## So, can an LLM do data science?

This experiment supports a more nuanced answer than “yes” or “no.”

The LLM successfully handled the major stages of the workflow:

1. Dataset inspection
2. Data-quality analysis
3. Target-leakage detection
4. Cleaning
5. Exploratory analysis
6. Hypothesis formation
7. Feature engineering
8. Baseline creation
9. Model training
10. Model comparison
11. Quantitative evaluation
12. Error analysis
13. Feature importance
14. Visualization
15. Limitations and recommendations

The strongest evidence is not the final MAE.

It is that decisions made early in the project were later validated by the model.

Distance mattered in EDA and became the strongest final feature.

Time mattered in controlled EDA and became the second-most-important feature.

A skewed target motivated a log-target experiment that achieved the lowest MAE.

Long-trip errors identified during evaluation aligned with known missing information such as traffic and exact route data.

That continuity is what a real data-science workflow should produce.

---

## Final result

The project went from:

**1,458,644 raw trips**

to:

**1,454,198 cleaned trips**

to:

**290,840 held-out test trips**

to a final model with:

- **3.10-minute MAE**
- **4.96-minute RMSE**
- **0.796 R²**

Compared with the median baseline, MAE fell from **7.41 minutes to 3.10 minutes**—roughly a **58% reduction**.

The model is not production-ready, and the experiment does not prove that an LLM should replace a data scientist.

What it does show is that, with access to the actual data and an execution environment, a language model can do substantially more than write snippets of Python.

It can participate in a complete, evidence-driven analytical workflow.

---

## What I would test next

If I continued the project, I would prioritize:

1. A time-based validation split
2. Actual road-network distance
3. Historical traffic data
4. Weather features
5. Spatial neighborhood clustering
6. Hyperparameter optimization
7. XGBoost / LightGBM / CatBoost comparisons
8. A separate strategy for unusually long trips

Those experiments would test whether the remaining errors come from model limitations or simply from information that is absent from the current dataset.
