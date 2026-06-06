export default function Sidebar() {
  return (
    <div className="bg-gray-900 text-white w-64 min-h-screen p-4">
      <ul>
        <li className="py-2 hover:bg-gray-700 cursor-pointer">Dashboard</li>
        <li className="py-2 hover:bg-gray-700 cursor-pointer">Alerts</li>
        <li className="py-2 hover:bg-gray-700 cursor-pointer">Reports</li>
      </ul>
    </div>
  );
}