import React from 'react';
import { steelPlants } from '../data/steelPlants';

export default function Reports() {
  const reports = [
    { metric: 'Avg. Rail Delay', value: `${(Math.random() * 20).toFixed(1)} hrs`, risk: 'High' },
    { metric: 'Critical Stock Plant', value: steelPlants[Math.floor(Math.random() * steelPlants.length)].name, risk: 'Severe' },
    { metric: 'Max Coal Consumer', value: steelPlants[Math.floor(Math.random() * steelPlants.length)].name, risk: 'Moderate' },
    { metric: 'Avg. Capacity Util.', value: `${(Math.random() * 20 + 70).toFixed(1)}%`, risk: 'Stable' },
  ];

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold">Performance Reports</h1>
      <div className="overflow-x-auto mt-4">
        <table className="min-w-full bg-white border rounded-lg shadow">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-2 px-4 border-b">Metric</th>
              <th className="py-2 px-4 border-b">Value</th>
              <th className="py-2 px-4 border-b">Status</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r, i) => (
              <tr key={i} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{r.metric}</td>
                <td className="py-2 px-4 border-b">{r.value}</td>
                <td className="py-2 px-4 border-b">{r.risk}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
