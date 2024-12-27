# Publications Data Pipeline ('Newton') 📰 🌃

A data pipeline project dedicated to the extraction &amp; analysis of headline data from famous publications such as the [New York Times](https://developer.nytimes.com/)

## Background 👓 

The origin of this project stems from an interest in analysing reporting trends (in news headlines) across various media outlets. I was always curious about whether I could build an algorithm to effectively compute which 'topics' are trending within any given time horizon - it turns out that you *can* achieve this by fitting a [logistic function](https://en.wikipedia.org/wiki/Logistic_function) to the appropriate dataset.

Luckily, outlets like the New York Times ("NYT") kindly provide an [API service](https://developer.nytimes.com/) completely free of charge which, amongst other things, can be used to extract data on historical article headlines. 

To keep things simple, the scope of this project is limited to NYT (for now).

## Architecture

<div style="text-align: center;"> 
  <img src="https://github.com/user-attachments/assets/ad866ef4-634d-4854-8172-fd5948f21bf4" alt="Diagram">
</div>
