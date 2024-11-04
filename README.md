# Personal AI Assistant

## Overview
This project is a React Native-based mobile application designed to enhance user experience by providing an intuitive interface for managing personal data and interacting with an AI assistant. The app features two main sections:
- **Home Page**: A secure area where users can store, add, and edit personal information such as contact details.
- **AI Chat Page**: A personal AI assistant that helps users perform various tasks, from answering questions to scheduling meetings and sending emails.

## Features
- **User-Friendly Interface**: Easy navigation and management of personal data.
- **Secure Data Management**: Store and edit personal and contact information directly in the app.
- **AI-Driven Assistance**: A personal AI chatbot for handling diverse tasks such as answering queries, reading PDF content, scheduling meetings, and sending emails.
- **Integration with Google Services**: Utilizes Gmail, Google Calendar, and Custom Search API for advanced task automation.

## Prerequisites
Before running the project, ensure you have the following:

1. **Environment Variables**:
   - `OPENAI_API_KEY`
   - `GOOGLE_CSE_ID`
   - `GOOGLE_API_KEY`
   - Add these keys in a `.env` file inside the `backend` folder.

2. **Google Services**:
   - **Enable** the following APIs:
     - **Gmail API**
     - **Google Calendar API**
     - **Custom Search API**
   - **Create** an API key and **OAuth Client ID** and complete the setup on the OAuth consent screen.

3. **Expo Setup**:
   - Install Expo CLI by running:
     ```bash
     npm install -g expo-cli
     ```
   - Run `npm install` inside the `frontend` folder to install necessary dependencies.

## Getting Started

### Backend Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
2. Create a `.env` file with the following content:
    ```bash
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_CSE_ID=your_google_cse_id
    GOOGLE_API_KEY=your_google_api_key
    ```
3. Run the server:
    ```bash
    python app.py
    ```
### Frontend Setup
1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
2. Install dependencies:
    ```bash
    npm install
    ```
3. Run the Expo development server:
    ```bash
    npx expo start
    ```
