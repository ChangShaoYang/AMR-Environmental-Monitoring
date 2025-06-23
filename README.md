# 🌱 Temperature & Humidity Mapping Robot for Smart Greenhouse

## 🧠 Overview
This project integrates a temperature 🌡️ and humidity 💧 sensor with an autonomous mobile robot 🤖 to monitor environmental conditions in the **NTU Smart Greenhouse**.  
The robot utilizes **SLAM** to build a map 🗺️ and navigates using the **A\*** path planning algorithm.  
During patrol, the robot and sensors collect data used to generate spatiotemporal **contour maps** using **Gaussian Process Regression (GPR)** in **MATLAB**.

---

## 🏗️ System Architecture

- **Mobile Robot** 🤖  
  Performs autonomous navigation using SLAM and A*.

- **Sensor Module** 📡  
  A DHT22 temperature and humidity sensor connected to an ESP32.

- **Communication** 📶  
  ESP32, robot, and laptop are connected to the same Wi-Fi network.  
  Real-time data transmission is achieved using the **UDP protocol**, ensuring lightweight and efficient delivery of sensor and position data.

---

## 🔁 Workflow

1. **SLAM Mapping** 🗺️  
   The robot constructs a 2D map of the greenhouse.

2. **Path Planning** 📍  
   A* algorithm determines optimal patrol routes.

3. **Data Collection** 📊  
   - ESP32 records temperature and humidity.  
   - Robot logs (x, y) position and timestamp.

4. **Data Transmission** 🌐  
   - Sensor and robot data are transmitted to the laptop using **UDP over Wi-Fi**.  
   - Ensures fast, connectionless communication suitable for real-time operation.

5. **Data Processing (in MATLAB)** 🧮  
   - Combine (x, y, time, temp) to train a GPR model.  
   - Use MATLAB to predict temperature across the greenhouse over time.

6. **Visualization (in MATLAB)** 🎨  
   - Generate contour maps 🌀 at various time points.  
   - Export an animated GIF 📽️ to visualize environmental changes over time.

---

## 🧾 Output

- 📍 **Contour Maps**: Spatial temperature distributions.
- 🌀 **Animated GIF**: Visualizing changes over time (generated via MATLAB).

---

## 🔬 Applications

- Real-time **microclimate monitoring**
- Smart greenhouse **automation & control**
- Environmental **data-driven research**
