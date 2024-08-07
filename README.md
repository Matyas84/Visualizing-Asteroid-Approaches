# Visualizing-Asteroid-Approaches
# Project_Horák_Lebeda

This is a repository for our Data Processing in Python project. Collaborative work of Matyáš Horák and Matyáš Lebeda.

## Visualizing Asteroid Approaches

The objective of this project is to create an interactive visualization tool that allows users to explore and understand the behavior and characteristics of asteroids that approach Earth. Using historical and real-time data fetched from NASA’s NeoWs API, the tool provides dynamic and interactive visualizations.

## Data Source

The primary data source for this project is the Asteroids - NeoWs API provided by NASA (https://api.nasa.gov/). This API offers comprehensive data about near-Earth objects (NEOs), including their size, velocity, close approach data, and orbital paths.

## Project Description

The project is divided into two main parts:

1. **Data Collection and Processing**: Fetching data from NASA’s NeoWs API, cleaning, and preparing it for visualization.
2. **Data Visualization and Interactive Dashboard**: Creating interactive visualizations to analyze asteroid data using Dash to allow users to interact with the visualizations.

### Technology Stack

- **Backend**: Python
- **Data Processing**: Pandas and NumPy
- **Visualization**: Plotly and Dash for interactive web applications

The dashboard features a responsive design for various devices, automatic data updates, and a user guide for navigating and understanding the visualizations.

### Project Structure

```plaintext
│ .gitignore                      # Git ignore file
│ README.md                       # Guide to our project code and structure
│ Visualization.py                # Main application script with data visualization
│ nasa.py                         # Script to interact with NASA API and fetch data
│ requirements.txt                # Required dependencies
```

### Application Components

- **Date Picker**: Allows users to select a date range for which the asteroid data is fetched and displayed.
- **Histogram and Box Plot Tab**: Visualizes the distribution of asteroid data (e.g., relative velocity, diameter) using histograms and box plots.
- **Scatter Plot Tab**: Compares asteroid sizes against their velocity and their magnitude, with options to filter by hazardous status and size.
- **Bar Chart Tab**: Displays the daily count of asteroids, with options to filter by hazardous status.

Tab Instructions are included on each tab for guidance and further understanding.

### Using the Application

1. **Clone the Repository**: Start by cloning the repository to your local machine.

    ```bash
    git clone https://github.com/Matyas84/Visualizing-Asteroid-Approaches.git
    ```

2. **Install Dependencies**: Open the folder you chose as your desired destination in Visual Studio Code and install the required dependencies using pip in your terminal.

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**: Execute the `Visualization.py` script to start the Dash application.

    ```bash
    python Visualization.py
    ```

4. **Access the Application**: Web browser with the interactive dashboard will be opened automatically. Alternatively, you can use the link in the terminal or open your web browser and go to `http://127.0.0.1:8050/`.

5. **Key insert**: You will have to obtain your own API key via https://api.nasa.gov/. To generate your API Key fill in the required fields, namely your first name, last name, email and optionally how you intend to use the API and then click the signup button. Your API key will be e-mailed to you. Insert your API key into the insert column on top of the the dash application.

6. **Using the Application** Follow the instructions on the dash app to use individual pages. You will always start by selecting the desired dates.

## Concluding remarks

The project structure and components mentioned above are tailored to provide users with an interactive and insightful experience in exploring asteroid approaches using data from NASA's NeoWs API. By following the steps under "Using the Application," users can easily set up and run the application locally to start analyzing trends and derive insights about near-Earth objects.Running the application locally ensures that users have full control over the environment and dependencies, providing a seamless and efficient experience.

While it is theoretically possible to deploy such applications online, there are significant challenges and limitations, especially when considering free hosting solutions. For instance, GitHub Pages is a popular platform for hosting static websites but it does not support running server-side applications like Dash. This limitation makes it unsuitable for hosting interactive Dash applications.

Commercial hosting solutions such as Heroku and AWS provide robust platforms for deploying Dash applications. However, these services often come with costs associated with sustained usage.

---

Matyáš Horák and Matyáš Lebeda