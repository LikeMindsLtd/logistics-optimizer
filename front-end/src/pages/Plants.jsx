import React from 'react';

export default function Plants() {
  const plants = [
    { name: 'Bhilai', utilization: 69.29, stock: 45280.57 },
    { name: 'Durgapur', utilization: 65.23, stock: 28497.4 },
    { name: 'Rourkela', utilization: 78.63, stock: 54388.25 },
  ];

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold">Steel Plant Performance & Risk</h1>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border rounded-lg shadow">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-2 px-4 border-b text-left">Plant</th>
              <th className="py-2 px-4 border-b text-left">Utilization (%)</th>
              <th className="py-2 px-4 border-b text-left">Stock (tonnes)</th>
            </tr>
          </thead>
          <tbody>
            {plants.map((p) => (
              <tr key={p.name} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{p.name}</td>
                <td className="py-2 px-4 border-b">{p.utilization.toFixed(2)}</td>
                <td className="py-2 px-4 border-b">{p.stock.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
