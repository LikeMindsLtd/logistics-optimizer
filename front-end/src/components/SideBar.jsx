import { NavLink, Link } from "react-router-dom";

const Sidebar = () => {
  const navItems = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Plants", path: "/plants" },
    { name: "Trains", path: "/trains" },
    { name: "Ports", path: "/ports" },
    { name: "Vessels", path: "/vessels" },
    { name: "Optimization", path: "/optimization" },
    { name: "Data Management", path: "/data-management" },
  ];

  return (
    <nav className="w-56 bg-gray-800 text-gray-200 p-5 h-screen relative">
      <h2 className="text-3xl font-bold mb-4 text-white">Logistics Optimizer</h2>
      <ul className="list-none p-0">
        {navItems.map((item) => (
          <li key={item.path} className="my-2.5">
            <NavLink
              to={item.path}
              className={({ isActive }) =>
                `no-underline ${
                  isActive
                    ? "text-blue-400 font-bold"
                    : "text-gray-200 hover:text-blue-200"
                }`
              }
            >
              {item.name}
            </NavLink>
          </li>
        ))}
      </ul>
      <div className="absolute bottom-5">
        <Link to="/logout" className="no-underline text-red-500">
          Logout
        </Link>
      </div>
    </nav>
  );
};

export default Sidebar;