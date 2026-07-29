# engagement-analyzer
# CampaignLens

CampaignLens is a Python and Flask web application that uses the YouTube Data API v3 to collect, analyze, and visualize the performance of marketing and promotional videos.

Users can search for a brand, company, product, or advertising campaign. CampaignLens retrieves related YouTube videos and analyzes metrics such as views, likes, comments, engagement rate, publication date, and title length. The results are displayed through summary statistics, tables, and visualizations.

## Features

* Search for promotional videos using a brand or campaign keyword
* Retrieve public video data from the YouTube Data API
* Collect video titles, channels, publication dates, views, likes, and comments
* Save collected data in a CSV file
* Calculate engagement rates and other performance statistics
* Compare the performance of different videos
* Generate charts using Matplotlib
* Display results through a Flask web interface
* Download or review the collected dataset

## Technologies Used

* Python
* Flask
* YouTube Data API v3
* Pandas
* NumPy
* Matplotlib
* HTML
* CSS
* CSV

## Project Structure

```text
campaignlens/
│
├── app.py
├── youtube_api.py
├── analysis.py
├── requirements.txt
├── README.md
│
├── data/
│   └── videos.csv
│
├── static/
│   ├── style.css
│   └── charts/
│
└── templates/
    ├── index.html
    └── results.html
```

## How It Works

1. The user enters a brand or campaign keyword.
2. The application sends a request to the YouTube Data API.
3. The API returns related videos and their public statistics.
4. The collected information is cleaned and saved in a CSV file.
5. Python analyzes the video performance data.
6. Matplotlib generates charts based on the selected metrics.
7. Flask displays the results in the web interface.

## Data Collected

CampaignLens may collect the following information for each video:

* Video title
* Video ID
* Channel name
* Publication date
* View count
* Like count
* Comment count
* Video duration
* Thumbnail URL
* Video description
* Title length

## Data Analysis

The application calculates and compares several performance measurements, including:

* Average views
* Average likes
* Average comments
* Engagement rate
* Most-viewed videos
* Most-engaging videos
* Title length versus engagement
* Publication date versus performance

The engagement rate is calculated as:

```text
Engagement Rate = ((Likes + Comments) / Views) × 100
```

Videos with zero views are handled separately to prevent division errors.

## Visualizations

CampaignLens can generate visualizations such as:

* Views by video
* Likes by video
* Comments by video
* Engagement rate by video
* Likes versus views
* Title length versus engagement rate
* Video performance by publication date

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/campaignlens.git
cd campaignlens
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment on macOS or Linux:

```bash
source venv/bin/activate
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install the required packages

```bash
pip install -r requirements.txt
```

A sample `requirements.txt` file may include:

```text
Flask
google-api-python-client
pandas
numpy
matplotlib
python-dotenv
isodate
```

## YouTube API Setup

1. Open the Google Cloud Console.
2. Create a new Google Cloud project.
3. Enable the YouTube Data API v3.
4. Create an API key.
5. Create a file named `.env` in the main project folder.
6. Add your API key:

```text
YOUTUBE_API_KEY=your_api_key_here
```

Do not upload your `.env` file or API key to GitHub.

Add the following line to `.gitignore`:

```text
.env
```

## Running the Application

From the main project directory, run:

```bash
python app.py
```

Then open the local address shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

## Using CampaignLens

1. Enter a keyword such as:

```text
Nike commercial
Apple advertisement
Sephora campaign
```

2. Select the number of videos to retrieve.
3. Select a sorting or analysis option.
4. Click the search or analyze button.
5. Review the video data and summary statistics.
6. View the generated charts.
7. Download the collected data if the option is available.

## Interface

The application contains at least two main pages:

### Search Page

The search page allows users to:

* Enter a campaign or brand keyword
* Choose the number of results
* Select a sorting option
* Start the search

### Results Page

The results page displays:

* Video statistics
* Summary information
* A table of collected data
* Metric-selection options
* Generated visualizations
* A CSV download option

## Team Responsibilities

### Partner 1: Data Collection and Organization

* Set up the YouTube Data API
* Retrieve video data
* Clean and organize the results
* Save data into CSV or JSON format
* Build the search page

### Partner 2: Analysis and Visualization

* Load the collected data
* Calculate performance statistics
* Calculate engagement rates
* Generate Matplotlib charts
* Build the results page

### Shared Responsibilities

* Connect the Flask pages
* Test the application
* Handle errors and missing data
* Write documentation
* Prepare the final presentation

## Error Handling

The application should handle situations such as:

* Missing or invalid API keys
* Empty search terms
* No videos found
* Missing likes or comments
* API quota errors
* Internet connection problems
* Videos with zero views
* Missing CSV files

## Future Improvements

Possible future updates include:

* Comparing multiple brands at once
* Adding interactive Plotly charts
* Supporting date-range filters
* Adding sentiment analysis for video comments
* Analyzing video descriptions and keywords
* Adding thumbnail image analysis
* Supporting additional platforms
* Adding machine-learning performance predictions
* Allowing users to save previous searches
* Deploying the application online

## Ethical Considerations

CampaignLens only uses publicly available YouTube information provided through the official YouTube Data API. The application does not collect private user information or attempt to access private advertising accounts.

The results should not be treated as proof that one video characteristic directly causes better performance. Engagement can be influenced by many factors, including audience size, advertising budget, brand popularity, upload timing, and external promotion.

## Authors

* Khushi Bakshi
* 

## License

This project was created for educational purposes as part of the CS 122 final project.
