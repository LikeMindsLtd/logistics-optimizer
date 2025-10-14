import React, { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { Link } from "react-router-dom";

const API_BASE = "http://localhost:8000/api/main/v1/data"; // update with your API

const MetricCard = ({ title, value, unit, color }) => (
  <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm hover:shadow-md transition">
    <h3 className="text-gray-600 font-medium">{title}</h3>
    <p className={`text-3xl font-bold ${color}`}>{value}</p>
    <p className="text-xs text-gray-400">{unit}</p>
  </div>
);

const Dashboard = () => {
  const [plants, setPlants] = useState([]);
  const [ports, setPorts] = useState([]);
  const [logistics, setLogistics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      const [plantRes, portRes, logisticsRes] = await Promise.all([
        fetch(`${API_BASE}/plants`),
        fetch(`${API_BASE}/ports`),
        fetch(`${API_BASE}/logistics`),
      ]);

      if (!plantRes.ok || !portRes.ok || !logisticsRes.ok) {
        throw new Error("Failed to fetch data from API.");
      }

      const [plantData, portData, logisticsData] = await Promise.all([
        plantRes.json(),
        portRes.json(),
        logisticsRes.json(),
      ]);

      // Ensure unique plants by plant_name
      const uniquePlants = Array.isArray(plantData.data)
        ? Array.from(new Map(plantData.data.map(p => [p.plant_name, p])).values())
        : [];

      // Ensure unique logistics types
      const uniqueLogistics = Array.isArray(logisticsData.data)
        ? Array.from(new Map(logisticsData.data.map(l => [l.type, l])).values())
        : [];

      setPlants(uniquePlants);
      setPorts(Array.isArray(portData.data) ? portData.data : []);
      setLogistics(uniqueLogistics);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch data from API.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, []);

  if (loading)
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center p-8 bg-white rounded-xl shadow-2xl">
          <span className="text-lg text-gray-600 font-medium">
            Loading data...
          </span>
        </div>
      </div>
    );

  const displayPorts = ports.slice(0, 4);

  const totalPlants = plants.length;
  const totalPorts = displayPorts.length;
  const totalLogistics = logistics.length;

  const totalCapacity = plants.reduce(
    (sum, p) => sum + (parseFloat(p.max_operating_capacity_mtpa) || 0),
    0
  );
  const avgUtilization =
    plants.reduce((sum, p) => sum + (parseFloat(p.stock_utilization_percent) || 0), 0) /
    (plants.length || 1);

  const stockChartData = plants.map((p) => ({
    name: p.plant_name,
    coal: parseFloat(p.coal_eod_stock_tonnes) || 0,
    limestone: parseFloat(p.limestone_eod_stock_tonnes) || 0,
  }));

  const utilizationChartData = plants.map((p) => ({
    name: p.plant_name,
    utilization: parseFloat(p.stock_utilization_percent) || 0,
  }));

  return (
    <div className="max-w-7xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2 text-gray-800">
        Logistics Dashboard
      </h1>
      <p className="text-gray-500 mb-8 text-base">
        Overview of plants, ports, and logistics
      </p>

      {error && (
        <div className="mb-8 p-3 text-sm bg-yellow-100 border border-yellow-400 text-yellow-700 rounded-lg">
          <p className="font-semibold">Data Warning:</p>
          <p>{error}</p>
        </div>
      )}

      {/* Metrics */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-10">
        <Link to="/plants">
          <MetricCard
            title="Total Plants"
            value={totalPlants}
            unit="Unique Facilities"
            color="text-indigo-600"
          />
        </Link>
        <Link to="/ports">
          <MetricCard
            title="Total Ports"
            value={totalPorts}
            unit="Operational"
            color="text-blue-600"
          />
        </Link>
        <MetricCard
          title="Total Capacity"
          value={`${totalCapacity.toFixed(1)} MTPA`}
          unit="Across Plants"
          color="text-green-600"
        />
        <MetricCard
          title="Total Logistics"
          value={totalLogistics}
          unit="Unique Types"
          color="text-orange-600"
        />
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Stock Levels (Coal vs Limestone)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stockChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="coal" fill="#4f46e5" name="Coal Stock (t)" />
              <Bar dataKey="limestone" fill="#f97316" name="Limestone Stock (t)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Plant Stock Utilization (%)
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={utilizationChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="utilization"
                stroke="#10b981"
                strokeWidth={3}
                dot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Plant Table */}
      <div className="bg-white p-6 mt-8 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold mb-4 text-gray-700">
          Plant Performance Summary
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-gray-100 text-gray-700">
                <th className="p-3 text-left">Plant Name</th>
                <th className="p-3 text-left">Capacity (MTPA)</th>
                <th className="p-3 text-left">Stock Utilization (%)</th>
                <th className="p-3 text-left">Coal Stock (t)</th>
                <th className="p-3 text-left">Limestone Stock (t)</th>
                <th className="p-3 text-left">Steel Exported (t)</th>
              </tr>
            </thead>
            <tbody>
              {plants.map((p, idx) => (
                <tr key={idx} className="border-b hover:bg-gray-50 transition-colors">
                  <td className="p-3 font-medium">{p.plant_name}</td>
                  <td className="p-3">{p.max_operating_capacity_mtpa}</td>
                  <td className="p-3">{p.stock_utilization_percent}</td>
                  <td className="p-3">{p.coal_eod_stock_tonnes}</td>
                  <td className="p-3">{p.limestone_eod_stock_tonnes}</td>
                  <td className="p-3">{p.steel_exported_tonnes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ports */}
      <div className="bg-white p-6 mt-8 rounded-xl shadow-md">
        <h2 className="text-lg font-semibold mb-4 text-gray-700">
          Major Ports
        </h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {displayPorts.map((port, i) => (
            <Link
              key={i}
              to="/ports"
              className="p-4 bg-gray-50 rounded-lg shadow hover:shadow-md transition block"
            >
              <h3 className="text-lg font-semibold text-gray-800 mb-1">
                {port.port_name}
              </h3>
              <p className="text-sm text-gray-600">
                <strong>Status:</strong> {port.status}
              </p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
