import React from 'react';
import { trainLogistics } from '../data/trainLogistics';

export default function Trains() {
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold">Train Logistics & Rake Schedules</h1>
      <p className="text-gray-600">Shows scheduled trains, cargo types, and capacity details.</p>

      <div className="overflow-x-auto mt-4">
        <table className="min-w-full bg-white border rounded-lg shadow">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-2 px-4 border-b">Train Name</th>
              <th className="py-2 px-4 border-b">Rake No.</th>
              <th className="py-2 px-4 border-b">Route</th>
              <th className="py-2 px-4 border-b">Cargo Type</th>
              <th className="py-2 px-4 border-b">Wagon Type</th>
              <th className="py-2 px-4 border-b">Rake Size</th>
              <th className="py-2 px-4 border-b">Capacity (tons)</th>
              <th className="py-2 px-4 border-b">Frequency</th>
            </tr>
          </thead>
          <tbody>
            {trainLogistics.map((train, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{train.trainName}</td>
                <td className="py-2 px-4 border-b">{train.rakeNo}</td>
                <td className="py-2 px-4 border-b">{train.route}</td>
                <td className="py-2 px-4 border-b">{train.cargoType.join(', ')}</td>
                <td className="py-2 px-4 border-b">{train.wagonType}</td>
                <td className="py-2 px-4 border-b">{train.rakeSize}</td>
                <td className="py-2 px-4 border-b">{train.capacity_tons.toLocaleString()}</td>
                <td className="py-2 px-4 border-b">{train.frequency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
