import React, { useState, useEffect } from 'react';
import logisticsData from '../data/logisticsData';

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    setData(logisticsData);
  }, []);

  if (!data) return <div className="text-center mt-20 text-gray-500">Loading dashboard data...</div>;

  const totalPlants = data.steelPlants.length;
  const totalRakes = data.trainLogistics.length;
  const totalVesselCapacity = data.importVessels.reduce((sum, v) => sum + (parseInt(v.capacityDWT) || 0), 0);
  const allPorts = [...new Set(data.portToPlantLogistics.map(p => p.port))];

  return (
    <div className="max-w-7xl mx-auto my-10 px-4">
      <h1 className="text-3xl font-bold text-center mb-2">Logistics Optimizer Dashboard</h1>
      <p className="text-center text-gray-500 mb-8">
        A quick overview of key metrics for the steel supply chain.
      </p>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Steel Plants */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Steel Plants Overview</h2>
          <p className="mb-4">Total Plants: <span className="font-bold">{totalPlants}</span></p>
          <ul className="space-y-2">
            {data.steelPlants.map((plant, i) => (
              <li key={i} className="border-b pb-1">
                <span className="font-bold">{plant.name}</span> - <span className="text-gray-500">{plant.location}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Transportation Assets */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Transportation Assets</h2>
          <p className="mb-4">Operational Train Rakes: <span className="font-bold">{totalRakes}</span></p>
          <ul className="space-y-2">
            {data.trainLogistics.slice(0, 5).map((train, i) => (
              <li key={i} className="border-b pb-1">
                <span className="font-bold">{train.route}</span> Rake ({train.rakeNo})
              </li>
            ))}
            <li className="text-gray-400">...and more</li>
          </ul>
        </div>

        {/* Import & Port Status */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Import & Port Status</h2>
          <p className="mb-4">Total Vessel DWT Capacity: <span className="font-bold">{totalVesselCapacity.toLocaleString()}</span></p>
          <ul className="space-y-2">
            <li>
              <span className="font-semibold">Active Ports:</span> <span className="text-gray-500">{allPorts.join(', ')}</span>
            </li>
            <li>
              <span className="font-semibold">Major Import Items:</span> <span className="text-gray-500">Limestone, Coal, Steel Coils</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
