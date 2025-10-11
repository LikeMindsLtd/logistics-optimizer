import React from 'react';
import data from '../data/logisticsData.js';

export default function Ports() {
  const ports = [
    { name: 'Haldia', stock: 52000, capacity: 100000 },
    { name: 'Paradip', stock: 85000, capacity: 120000 },
    { name: 'Visakhapatnam', stock: 30000, capacity: 80000 },
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold mb-4">Port Inventory & Rail Links</h1>
      <div className="grid md:grid-cols-3 gap-6">
        {ports.map((port) => (
          <div key={port.name} className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-2">{port.name}</h2>
            <p>Stock: {port.stock.toLocaleString()} MT</p>
            <p>Capacity: {port.capacity.toLocaleString()} MT</p>
            <p>Utilization: {((port.stock / port.capacity) * 100).toFixed(1)}%</p>
          </div>
        ))}
      </div>
    </div>
  );
}
