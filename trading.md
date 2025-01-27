# TradingPal Updates

This document outlines the changes and updates for the TradingPal backtesting system.

## Overview

The TradingPal backtesting system is undergoing several enhancements to improve its functionality, user interface, and integration with external services. These updates include:

*   Refactoring the `indicators.py` file to integrate with a database model.
*   Implementing an indicator dropdown in the UI.
*   Creating a Gemini AI agent for processing user requests.
*   Updating the sidebar/side section to display trading strategies and indicators.
*   Enhancing trading strategy data and backtesting features.
*   Maintaining Oanda integration for data retrieval.

## File Structure and Responsibilities

*   **`main.py`:** Contains the main application logic and API endpoint for triggering backtesting.
*   **`trading.py`:** Handles loading historical data from OANDA.
*   **`indicators.py`:** Calculates technical indicators (currently) and will be repurposed to manage indicator loading and saving.
*   **`models.py`:** Defines the database models, including the new model for indicators.
*   **`backtest.html`:** Frontend template for the backtesting interface.
*   **`backtest.js`:** JavaScript code for handling user interactions and displaying results on the frontend.

## Current Status

| Feature                 | Status        | Notes                                                                                                                                      |
| :---------------------- | :------------ | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `indicators.py` Refactor | Complete      | Integrated database model, repurposed for loading/saving indicators.                                                                        |
| Indicator Dropdown      | Complete      | Implemented dropdown list in UI.                                                                                                             |
| Gemini AI Agent         | In Progress   | Created agent to process user requests for trading strategies and indicators.                                                               |
| Sidebar/Side Updates    | To Do         | Display strategies/indicators, add toggle for switching views.                                                                              |
| Trading Strategy Data   | In Progress   | Includes strategy name, author, code, currency pair, timeframe, backtest results.                                                            |
| Backtesting Enhancements | In Progress   | Allows re-backtesting with different parameters, displays results in a basic format, needs popup and sidebar access.                           |
| Oanda Integration       | In Progress   | Maintain existing integration.                                                                                                             |
| `trading.md`            | In Progress   | Create and update this document to track changes, status, and to-do list.                                                                   |
| Database Model          | Complete      |  The indicators.py indicators are stored in a database model, allowing for future expansion. and repurpose indicators .py |

## Gemini AI Agent Integration Status

The Gemini AI agent integration for code generation is partially complete. Here's a breakdown of the current status:

**Completed:**

-   **Frontend Changes (`backtest.html`):**
    -   Added a "robot" icon button to the strategy code editor.
    -   Created a popup modal with a textarea for interacting with the agent and a button to send the prompt.
-   **Frontend Changes (`backtest.js`):**
    -   Implemented `setupModal()` to handle modal display and closing.
    -   Added a click event listener to the "robot" icon button to open the modal.
    -   Implemented functionality to send user input from the modal's textarea to the `/api/v1/querystrategyagent` endpoint.
    -   Added basic error handling for missing authentication tokens.
-   **Backend Changes (`main.py`):**
    -   Created a new endpoint `/api/v1/querystrategyagent` to handle code generation requests.
    -   Implemented a basic framework for receiving the prompt and generating a response using the Gemini AI model.
    -   Added a placeholder system prompt with instructions for the AI.

**In Progress:**

-   **Agent Logic:**
    -   The agent's logic for understanding user requests and generating code is still under development. The current implementation uses a basic prompt and doesn't fully utilize the available context or functions.
-   **Response Handling:**
    -   The `backtest.js` code now updates the strategy code editor with the generated code.
-   **Error Handling:**
    -   Error handling is basic and needs to be improved to handle various error scenarios gracefully.
-   **Testing:**
    -   Thorough testing of the integration is required to ensure it works as expected.

**Next Steps:**

-   Refine the Gemini AI agent's prompt and logic to improve code generation accuracy and handle a wider range of user requests.
-   Implement functionality in `backtest.js` to update the strategy code editor with the AI-generated code.
-   Add comprehensive error handling and logging to both the frontend and backend.
-   Conduct thorough testing of the integrated functionality.

## To-Do List

-   [x] **Investigate Codebase:** Thoroughly review `main.py`, `trading.py`, `indicators.py`, `backtest.html`, `backtest.js`, and `models.py` to understand current implementation.
-   [x] **Update `trading.md`:** Based on the investigation, update this document with detailed findings and a comprehensive to-do list.
-   [x] **Refactor `indicators.py`:**
    -   [x] Integrate database model for storing indicators (already done in `models.py`).
    -   [x] Modify `load_all_indicators()` to dynamically execute calculation code from the `Indicator` model.
    -   [x] Update `save_indicator_to_db()` to handle potential errors and edge cases.
    -   [x] Add error handling and logging to indicator calculation functions.
-   [x] **Implement Indicator Dropdown:**
    -   [x] Modify `backtest.html` to include a `select` element for the dropdown.
    -   [x] Modify `backtest.js` to populate the dropdown using the `/api/v1/indicators` endpoint (already implemented in `loadIndicators()`).
    -   [x] Update `backtest.js` to send the selected indicator to the backend during backtesting.
-   [ ] **Create Gemini AI Agent for Code Generation:**
    -   [x] Design the agent's architecture and integration points (modal on `backtest.html`, new endpoint `/api/v1/querystrategyagent`).
    -   [ ] Implement the agent's logic for understanding user requests related to strategy and indicator code.
        -   [ ] Create a new function in `main.py` (e.g., `handle_agent_request`) to handle agent interactions.
        -   [ ] Implement intent recognition logic within `handle_agent_request`.
        -   [ ] Implement entity extraction logic within `handle_agent_request`.
    -   [x] Create a new endpoint `/api/v1/querystrategyagent` in `main.py` to handle code generation requests.
    -   [ ] Integrate the Gemini AI model to generate code based on user input.
        -   [x] Update the agent to use a more comprehensive system prompt.
    -   [ ] Add error handling and logging.
-   [x] **Update `backtest.html`:**
    -   [x] Add a "robot" icon button to the strategy code editor.
    -   [x] Create a popup modal with a textarea for interacting with the agent.
-   [x] **Update `backtest.js`:**
    -   [x] Add a click event listener to the new button to display the modal.
    -   [x] Implement functionality to send user input from the modal's textarea to `/api/v1/querystrategyagent`.
        -   [x] Add code to retrieve authentication token from local storage.
        -   [x] Send the prompt to `/api/v1/querystrategyagent` with the token in the headers.
    -   [x] Handle the response from the agent and update the strategy code editor accordingly.
-   [ ] **Update Sidebar/Side Section:**
    -   [ ] Modify `backtest.html` to include a toggle for switching between strategies and indicators.
    -   [ ] Update `backtest.js` to dynamically display strategies or indicators based on the toggle state.
    -   [ ] Implement functionality to load a selected strategy into the form.
    -   [ ] Implement functionality to display backtest results when clicking on a strategy.
-   [ ] **Enhance Trading Strategy Data:**
    -   [x] Update the `Strategy` model in `models.py` to include fields for author name and backtest results (already partially done).
    -   [ ] Modify `main.py` to store and retrieve the new strategy data.
    -   [ ] Update `backtest.js` to handle the new strategy data.
-   [ ] **Improve Backtesting:**
    -   [ ] Modify `backtest_strategy` in `main.py` to accept parameters for re-backtesting (timeframe, currency pair, indicator).
    -   [ ] Update `backtest.js` to send these parameters during re-backtesting.
    -   [ ] Implement a centered popup for displaying backtest results (consider using a modal or a dedicated results page).
    -   [ ] Add a button or link in the sidebar to access the backtest results for each strategy.
-   [ ] **Maintain Oanda Integration:**
    -   [ ] Regularly test the Oanda integration to ensure continued functionality.
    -   [ ] Update dependencies if necessary.
    -   [ ] Monitor for any changes in the Oanda API that might affect the integration.
-   [ ] **Refactor `main.py`:**
    -   [ ] Break down large functions into smaller, more manageable functions.
    -   [ ] Improve error handling and logging throughout the file.
    -   [ ] Add comments and docstrings to enhance readability.
-   [ ] **Refactor `backtest.js`:**
    -   [ ] Break down large functions into smaller, more manageable functions.
    -   [ ] Improve error handling and user feedback.
    -   [ ] Add comments and documentation.
-   [ ] **Testing:**
    -   [ ] Write unit tests for `indicators.py`, `trading.py`, and other critical modules.
    -   [ ] Write integration tests for the API endpoints.
    -   [ ] Perform end-to-end testing of the backtesting process.
