# Web Vulnerability Scanner

## Project Overview
This project is a web vulnerability scanner that I built to demonstrate how common website security issues can be detected using a custom backend and a web-based frontend. The goal of this project is to show how frontend and backend systems communicate in a real application while performing automated security checks.

The scanner runs locally on the user’s computer and analyzes a target website for potential vulnerabilities. It is designed for educational purposes and focuses on understanding how scanning tools work rather than exploiting real systems.

-

## How the Project Works
The project is split into two main parts:

- A Python backend that performs the scanning logic
- A React frontend that provides a user interface

The backend handles requests, runs scans, and sends results back to the frontend. The frontend allows the user to start scans and view results in a clear, readable format.

The frontend and backend communicate using HTTP requests over different local ports.

-

## Technologies Used
- Python with Flask for the backend server
- Flask-CORS to allow frontend and backend communication
- JavaScript with React for the frontend interface
- Axios for API requests
- Node.js and npm for frontend dependencies

-

## Project Structure
