import React, { useState } from 'react';
import { trainLogistics } from '../data/trainLogistics';

export default function Optimization() {
  const [cost, setCost] = useState(0);
  const [rakes, setRakes] = useState(20);

  const simulateOptimization = () => {
    const totalTrains = trainLogistics.length;
    const result = ((totalTrains * rakes * (Math.random() * 2 + 0.5)) / 1000).toFixed(2);
    setCost(result);
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold">Logistics Optimization Simulation</h1>
      <p className="text-gray-600">Adjust parameters and run optimization scenarios.</p>

      <div className="mt-4">
        <label className="block mb-1 font-medium">Rake Availability:</label>
        <input
          type="number"
          value={rakes}
          onChange={(e) => setRakes(Number(e.target.value))}
          min="5"
          max="50"
          className="border rounded px-3 py-2 w-32"
        />
      </div>

      <button
        onClick={simulateOptimization}
        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Run Optimization
      </button>

      <p className="mt-4 text-lg">
        Estimated Cost: <strong>${cost}M</strong>
      </p>
    </div>
  );
}
