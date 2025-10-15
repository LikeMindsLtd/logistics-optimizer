import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const TRIGGER_URL = "http://localhost:5000/api/main/v1/trigger-training";
const STATUS_URL = "http://localhost:5000/api/main/v1/training-status";
const POLLING_INTERVAL = 3000;
const LOCAL_STORAGE_KEY = 'lastAiTrainRunTime';

export default function AITrainingTrigger() {
    const [trainingStatus, setTrainingStatus] = useState("Idle");
    const [statusMessage, setStatusMessage] = useState("Model training is currently inactive.");
    const [isPolling, setIsPolling] = useState(false); 
    const [isLoading, setIsLoading] = useState(false);
    
    // Initialize state by reading from Local Storage
    const [lastRunTime, setLastRunTime] = useState(
        localStorage.getItem(LOCAL_STORAGE_KEY)
    ); 

    // Function to fetch the current training status
    const fetchStatus = useCallback(async () => {
        try {
            const response = await axios.get(STATUS_URL);
            const status = response.data.status || "Unknown";
            const message = response.data.message || "Checking status...";

            setTrainingStatus(status);
            setStatusMessage(message);

            if (status === "Complete") {
                setIsPolling(false); 
                setTrainingStatus("Success");
                
                // --- LOCAL STORAGE PERSISTENCE ---
                const now = new Date().toLocaleString();
                setLastRunTime(now); 
                localStorage.setItem(LOCAL_STORAGE_KEY, now); // Save to local storage

                
            } else if (status === "Error" || status === "Idle") {
                setIsPolling(false); 
            } else if (status === "Training" || status === "Queued") {
                setIsPolling(true); 
            }
            
        } catch (error) {
            console.error("Failed to fetch training status:", error);
            setStatusMessage("Error connecting to AI server.");
            setTrainingStatus("Error");
            setIsPolling(false);
        }
    }, []); 

    useEffect(() => {
        fetchStatus(); // Check current training status
    }, [fetchStatus]); 


    // 2. Polling Effect
    useEffect(() => {
        if (!isPolling) {
            return;
        }
        
        const intervalId = setInterval(fetchStatus, POLLING_INTERVAL);
        return () => clearInterval(intervalId);
    }, [isPolling, fetchStatus]);


    // Function to trigger the training process
    const triggerTraining = async () => {
        setIsLoading(true);
        setStatusMessage("Triggering training...");
        setTrainingStatus("Queued");
        setLastRunTime(null); 

        try {
            await axios.post(TRIGGER_URL, {});
            setStatusMessage("Training triggered successfully. Starting polling...");
            setIsPolling(true); 
        } catch (error) {
            console.error("Failed to trigger training:", error.response?.data || error.message);
            setStatusMessage("Failed to trigger training. Check server logs.");
            setTrainingStatus("Error");
            setIsPolling(false); 
        } finally {
            setIsLoading(false);
        }
    };

    // Helper for button color/text based on status
    const getButtonClass = () => {
        if (isLoading || isPolling) return "bg-gray-500 cursor-not-allowed";
        if (trainingStatus === "Success") return "bg-green-500 hover:bg-green-600";
        if (trainingStatus === "Error") return "bg-red-500 hover:bg-red-600";
        return "bg-indigo-600 hover:bg-indigo-700";
    };

    return (
        <div className="border p-4 rounded shadow-sm space-y-3 bg-white">
            <h3 className="text-xl font-semibold text-indigo-700">AI Model Training</h3>
            
            {/* Display Last Run Time, retrieved from local storage on load */}
            {lastRunTime && (
                <div className="text-sm font-medium text-gray-700">
                    Last Successful Run: 
                    <strong className="text-green-600 ml-1">{lastRunTime}</strong>
                </div>
            )}

            <div className="flex items-center space-x-4">
                <button
                    onClick={triggerTraining}
                    disabled={isLoading || isPolling} 
                    className={`px-4 py-2 text-white font-medium rounded transition duration-150 ${getButtonClass()}`}
                >
                    {isLoading
                        ? "Sending Request..."
                        : isPolling 
                        ? "Training in Progress..."
                        : "Start New Training"}
                </button>
                <div className="flex flex-col">
                    <span className="text-sm font-medium text-gray-700">
                        Current Status: 
                        <strong className={`font-bold ml-1 ${
                            trainingStatus === "Success" ? "text-green-600" : 
                            trainingStatus === "Error" ? "text-red-600" : 
                            trainingStatus === "Idle" ? "text-gray-500" : "text-yellow-600"
                        }`}>
                            {trainingStatus}
                        </strong>
                    </span>
                    <span className="text-xs text-gray-500">{statusMessage}</span>
                </div>
            </div>
        </div>
    );
}