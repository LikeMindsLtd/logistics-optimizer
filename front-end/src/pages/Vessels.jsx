import React from 'react';
import { importVessels } from '../data/importVessels';

export default function Vessels() {
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-3xl font-bold">Vessels Schedule & Tracking</h1>
      <p className="text-gray-600">Displays vessels arriving at ports, cargo details, and live tracking info.</p>

      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border rounded-lg shadow">
          <thead className="bg-gray-100">
            <tr>
              <th className="py-2 px-4 border-b text-left">Vessel</th>
              <th className="py-2 px-4 border-b text-left">Port</th>
              <th className="py-2 px-4 border-b text-left">Cargo</th>
              <th className="py-2 px-4 border-b text-left">Capacity (DWT)</th>
              <th className="py-2 px-4 border-b text-left">Price (USD/ton)</th>
            </tr>
          </thead>
          <tbody>
            {importVessels.map((v, idx) => (
              <tr key={idx} className="hover:bg-gray-50">
                <td className="py-2 px-4 border-b">{v.shipName}</td>
                <td className="py-2 px-4 border-b">{v.port}</td>
                <td className="py-2 px-4 border-b">{v.item}</td>
                <td className="py-2 px-4 border-b">
                  {typeof v.capacityDWT === 'number'
                    ? v.capacityDWT.toLocaleString()
                    : v.capacityDWT}
                </td>
                <td className="py-2 px-4 border-b">{v.priceUSDPerTon}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
