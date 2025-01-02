# Logistic Growth

## Methodology

There are two types of trends that we want to focus on:

* **Growth**: which particular topics are becoming increasingly 'important' as time goes on?
* **Shrinkage**: which topics have fallen off the radar?

One possible way of modelling growth (or equivalently, shrinkage) is using a simple moving average.

However, the problem with a moving average is that it is too prone to sudden volatile movements.

Instead, we can model 'topic' trends through the use of a logistic growth (logistic regression) model. Logistic regression models are typically applied in the context of classification problems in machine learning. But, it might surprise some practitioners to know that this statistical model was originally employed in the biological domain.

In this context, it is used to model variables which exhibit an initial period of exponential growth followed by a period of plateau at a certain future point in time. The latter period of 'tailing off' is driven by some kind of constraint on the variable of interest. In epidemiology, for example, one can examine the initial phase of viral spread and note that it is indeed exponential but only up until a certain point - eventually, everyone who is infected either dies or people recover and gain immunity leading to a 'tailing off' in the initial spread.

Certain topics as reported in the media can be thought of in a similar way: for example, consider the coronavirus pandemic.

As the pandemic emerges some topics will become more newsworthy and increase exponentially up until a certain point: reporters cannot, of course, continue to discuss such topics at an exponential rate since there is a limited number of reporters at any one time and other topics will inevitably emerge to fill their place. 

Our plan is to regress an output variable, representing the relative frequency of a term in a given day, against time elapsed since the new year. With regards to the former, we can think of the number of times a given term appears in a given day as the number of 'successes' and the number of times that any term appears in a given day (i.e. the number of words we have for that day) as the number of 'trials'. This ratio is a basic indicator of term coverage.

## Model

More plainly, let *U*<sub>*t*</sub><sup>(*w*)</sup> denote the 'relative usage' of word *w* at time *t* - by 'relative usage' we mean how frequently word *w* is used relative to all other words at the same time *t*. Then *U*<sub>*t*</sub><sup>(*w*)</sup> is connected to the linear combination −(*β*<sub>0</sub><sup>(*w*)</sup> + *β*<sub>1</sub><sup>(*w*)</sup>*t*) by way of a [logistic transformation](https://en.wikipedia.org/wiki/Logistic_regression#Logistic_model).

The coefficient *β*<sub>1</sub><sup>(*w*)</sup> can be interpreted as the *rate* of growth (or shrinkage, if negative) associated with word *w*. Indeed, this formula is on a per-word (i.e. topic) basis.

## Exclusions

One important point to make here is that we don't want to include all words in our analysis - some words (such as 'Bolton' in regards to Trump's impeachment trial) appear a high number of times on one or two days then vanish thereafter. This type of term, from our point of view, is only going to create unnecessary noise in our algorithm fitting process so we want to exclude them. 

One way of doing this is to require that all words included in our analysis appear a certain number of times overall - I've gone with 50 as this seemed to provide the most fair results.

As another layer of validation though, I have also decided to store the 'relative standard error' (i.e. the ratio of the standard error to the absolute value of the growth coefficient - if this is high then it suggests a highly volatile topic) associated with the growth coefficient of each term and eliminate terms with a relative standard error of greater than e.g. 20%.

You can see this design choice in the file `src/db/init.sql` by examining the `model.output` DDL,

```sql
CREATE TABLE model.output (
    model_output_id SERIAL PRIMARY KEY,
    headline_term VARCHAR(50) NOT NULL,
    coef_intercept NUMERIC NOT NULL,
    coef_time NUMERIC NOT NULL,
    rse_time NUMERIC NOT NULL, -- relative standard error
    p_value_time NUMERIC NOT NULL,
    model_run_id INT NOT NULL,
    FOREIGN KEY (model_run_id) REFERENCES model.run(model_run_id)
);
```



