# GtaV121VatG's Network Traffic Monitor:

## Project Overview
This project is a network traffic monitor that I built to demonstrate how network data can be captured, analyzed, and displayed using a full stack application. The purpose of this project is to show how network activity can be monitored locally while connecting a backend system to a web based frontend.

The application runs on a local machine and is intended for educational use only. It focuses on understanding how network monitoring tools work rather than intercepting or modifying real traffic.

---

## How the Project Works
The project is divided into two main components:

- A Python backend that monitors and processes network traffic
- A React frontend that displays traffic data in a clear interface

The backend collects network information and exposes it through API endpoints. The frontend sends requests to the backend and updates the display in real time based on the data received.

The frontend and backend communicate using HTTP requests on different local ports.

---

## Technologies Used
- Python with Flask for the backend server
- Flask-CORS to allow cross origin communication
- JavaScript with React for the frontend interface
- Axios for API requests
- Node.js and npm for frontend dependencies

---

## Project Structure
