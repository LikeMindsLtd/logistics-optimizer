import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Use environment variable for base API URL
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/main/v1/data";

export default function Plants() {
  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [allLoaded, setAllLoaded] = useState(false);

  const PAGE_SIZE = 20; // Load 20 at a time

  // Safe numeric conversion
  const safeNumber = (val) => (isNaN(Number(val)) ? 0 : Number(val));

  const fetchPlants = async (pageNum) => {
    try {
      const res = await fetch(`${API_BASE}/plants?page=${pageNum}&limit=${PAGE_SIZE}`);
      if (!res.ok) throw new Error(`API Error: ${res.status} ${res.statusText}`);

      const data = await res.json();
      if (!data?.data || data.data.length === 0) {
        setAllLoaded(true);
        return;
      }
      setPlants((prev) => [...prev, ...data.data]);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch plant data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlants(page);
  }, [page]);

  const handleLoadMore = () => setPage((prev) => prev + 1);

  if (loading && plants.length === 0) {
    return <p className="p-6 text-gray-600">Loading plants data...</p>;
  }

  if (error) {
    return <p className="p-6 text-red-600">{error}</p>;
  }

  // Chart Data
  const stockChartData = plants.map((p) => ({
    name: p.plant_name,
    coal: safeNumber(p.coal_eod_stock_tonnes),
    limestone: safeNumber(p.limestone_eod_stock_tonnes),
  }));

  const utilizationChartData = plants.map((p) => ({
    name: p.plant_name,
    utilization: safeNumber(p.stock_utilization_percent),
  }));

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Steel Plant Performance & Risk</h1>

      {/* Coal vs Limestone Bar Chart */}
      <div className="bg-white p-6 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          Coal vs Limestone Stock (tonnes)
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stockChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip formatter={(value) => safeNumber(value).toLocaleString()} />
            <Bar dataKey="coal" fill="#4f46e5" name="Coal Stock" />
            <Bar dataKey="limestone" fill="#f97316" name="Limestone Stock" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Utilization Line Chart */}
      <div className="bg-white p-6 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">Plant Utilization (%)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={utilizationChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} />
            <YAxis />
            <Tooltip formatter={(value) => `${safeNumber(value).toFixed(2)}%`} />
            <Line
              type="monotone"
              dataKey="utilization"
              stroke="#10b981"
              strokeWidth={3}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Plants Table */}
       <div className="overflow-x-auto bg-white p-6 rounded-xl shadow-lg border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Detailed Plant Records</h2>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50">
                Plant
              </th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Utilization (%)
              </th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Coal Stock (tonnes)
              </th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Limestone Stock (tonnes)
              </th>
              <th className="py-3 px-4 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Steel Exported (tonnes)
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {plants.map((p) => {
              const util = safeNumber(p.stock_utilization_percent);
              const utilColor = util > 85 ? 'text-green-600 font-bold' : util < 50 ? 'text-red-600 font-bold' : 'text-yellow-600';

              return (
                <tr key={p.id} className="hover:bg-indigo-50/50 transition">
                  <td className="py-3 px-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white hover:bg-indigo-50/50">
                    {p.plant_name}
                  </td>
                  <td className={`py-3 px-4 whitespace-nowrap text-sm ${utilColor}`}>
                    {util.toFixed(2)}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-500">
                    {safeNumber(p.coal_eod_stock_tonnes).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-500">
                    {safeNumber(p.limestone_eod_stock_tonnes).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap text-sm text-gray-500">
                    {safeNumber(p.steel_exported_tonnes).toLocaleString()}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Load More Button */}
      {!allLoaded && (
        <div className="flex justify-center mt-4">
          <button
            onClick={handleLoadMore}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
}
